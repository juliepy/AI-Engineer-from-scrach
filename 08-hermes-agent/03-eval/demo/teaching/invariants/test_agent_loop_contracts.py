"""Agent-loop 行为契约测试（pytest）。

讲解要点：
  1. 写法对齐 Hermes CI：Test* 类 + 断言「数据之间的关系」，不断言某次实跑的具体数字。
  2. 测的对象是已保存的轨迹 JSON（messages + trace），不是现场调模型。
  3. 正例 from_02_agent_loop.json 应全部通过；负例 failure_run.json 应被检出失败。
  4. 不要写：api_calls == 7、tool 精确序列相等——那会在换模型后误报。

对照：AGENTS.md「Don't write change-detector tests」；
     hermes-study/tests/agent/test_prompt_caching.py。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from checkers import (
    check_budget_consistent,
    check_role_alternation,
    check_system_stable,
    check_tools_frozen,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
GOLDEN = FIXTURES / "from_02_agent_loop.json"
FAILURE = FIXTURES / "failure_run.json"

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
from scorer import score_case, tool_sequence_from_trace  # noqa: E402


def _load(path: Path) -> dict:
    """读 fixtures 下的轨迹 JSON，得到 messages / trace / budget 等字段。"""
    assert path.exists(), f"missing {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def golden_run() -> dict:
    """模块级加载正例一次：02 Agent Loop 实跑后保存的轨迹。"""
    return _load(GOLDEN)


@pytest.fixture(scope="module")
def failure_run() -> dict:
    """模块级加载负例一次：手写的错误轨迹，用来确认检查函数会失败。"""
    return _load(FAILURE)


class TestRoleAlternation:
    """检查 messages 里相邻两条的 role 是否合法。

    规则（与 checkers.check_role_alternation 一致）：
      - 允许连续 user（常见：历史最后一条 user + 本轮再 append 一条 user）
      - 允许连续 tool（一次回复多个 tool_calls 时会有多条 tool）
      - 不允许连续 assistant、连续 system
    """

    def test_golden_messages_ok(self, golden_run: dict) -> None:
        """正例：整段 messages 应通过 role 检查；失败时 detail 会指出第几条。"""
        ok, detail = check_role_alternation(golden_run["messages"])
        assert ok, detail

    def test_consecutive_user_allowed(self) -> None:
        """构造「user → user → assistant」：应通过，说明连续 user 是允许的。"""
        ok, detail = check_role_alternation(
            [
                {"role": "user", "content": "hist"},
                {"role": "user", "content": "current turn"},
                {"role": "assistant", "content": "ok"},
            ]
        )
        assert ok, detail

    def test_consecutive_assistant_rejected(self) -> None:
        """构造「assistant → assistant」：应失败，且 detail 含 consecutive role。"""
        ok, detail = check_role_alternation(
            [
                {"role": "user", "content": "q"},
                {"role": "assistant", "content": "a1"},
                {"role": "assistant", "content": "a2"},
            ]
        )
        assert not ok
        assert "consecutive role" in detail

    def test_failure_fixture_breaks_role(self, failure_run: dict) -> None:
        """负例文件里的 messages 已故意写成非法 role 序列，这里确认会被检出。"""
        ok, _ = check_role_alternation(failure_run["messages"])
        assert not ok


class TestPromptCacheInvariants:
    """检查同一次对话循环里，发给 API 的 system 与 tools 是否中途被改掉。

    Hermes 要求：同一 conversation 内 system prompt、tools schema 保持不变，
    这样 provider 才能复用 prompt cache。若中途改了，成本会上升。
    实现：看 trace 里每次 api_request 的 system_fingerprint / tool_names。
    """

    def test_golden_system_stable(self, golden_run: dict) -> None:
        """正例：每次 api_request 记录的 system 标识相同 → 通过。"""
        ok, detail = check_system_stable(golden_run["trace"])
        assert ok, detail

    def test_golden_tools_frozen(self, golden_run: dict) -> None:
        """正例：每次 api_request 的 tool_names 集合相同 → 通过。"""
        ok, detail = check_tools_frozen(golden_run["trace"])
        assert ok, detail

    def test_failure_system_drifts(self, failure_run: dict) -> None:
        """负例：trace 里后一次 api_request 的 system 标识与前一次不同 → 应失败。"""
        ok, _ = check_system_stable(failure_run["trace"])
        assert not ok

    def test_failure_tools_mutate_mid_loop(self, failure_run: dict) -> None:
        """负例：循环中途 tool_names 集合发生变化 → 应失败。"""
        ok, _ = check_tools_frozen(failure_run["trace"])
        assert not ok


class TestBudgetDiscipline:
    """检查预算相关字段是否互相矛盾。

    主要关系：
      - budget_used ≤ budget_max
      - exit_reason == budget_grace_call 时，api_calls 必须等于 budget_max + 1
        （预算用尽后再允许多调一次 API 收尾）
      - exit_reason == budget_exhausted 时，budget_used 应已达到 budget_max
    """

    def test_golden_budget_consistent(self, golden_run: dict) -> None:
        """正例整包字段交给 check_budget_consistent，应通过。"""
        ok, detail = check_budget_consistent(golden_run)
        assert ok, detail

    def test_golden_grace_means_one_extra_call(self, golden_run: dict) -> None:
        """若退出原因是 budget_grace_call，则断言 api_calls == budget_max + 1。

        这里测的是「grace 与多一次调用」的对应关系。
        不要写成 assert api_calls == 7：换模型后步数可能变，测试会误失败。
        """
        if golden_run.get("exit_reason") == "budget_grace_call":
            assert golden_run["api_calls"] == int(golden_run["budget_max"]) + 1

    def test_failure_budget_inconsistent(self, failure_run: dict) -> None:
        """负例预算字段互相矛盾（例如 grace 但 api_calls 不对），应失败。"""
        ok, _ = check_budget_consistent(failure_run)
        assert not ok


class TestToolExpectations:
    """检查轨迹里实际调用了哪些工具，用集合关系，不用精确顺序。

    正确写法：required ⊆ 实际工具集合；禁止某工具出现。
    错误写法：assert tool_sequence == ["todo", "web_search", ...]
             （顺序或次数一变，测试就挂，属于变更检测测试。）
    """

    def test_golden_has_required_tools_as_subset(self, golden_run: dict) -> None:
        """正例：实际工具集合必须包含 todo 和 web_search（子集关系）。"""
        tools = set(tool_sequence_from_trace(golden_run["trace"]))
        required = {"todo", "web_search"}
        assert required <= tools, f"missing {sorted(required - tools)}"

    def test_golden_does_not_require_exact_sequence(self, golden_run: dict) -> None:
        """正例：只要求序列里出现过 todo，且 web_search 至少一次；不要求整段序列相等。"""
        seq = tool_sequence_from_trace(golden_run["trace"])
        assert "todo" in seq
        assert seq.count("web_search") >= 1

    def test_failure_uses_forbidden_tool(self, failure_run: dict) -> None:
        """负例：轨迹里出现了 execute_code（本 demo 把它定为禁止工具）。"""
        tools = set(tool_sequence_from_trace(failure_run["trace"]))
        assert "execute_code" in tools


class TestOfflineCaseScoring:
    """用 scorer.score_case 做整 case 打分（与 run_eval_suite Layer B 同一套逻辑）。

    正例：九项 check 全通过 → passed == True。
    负例：passed == False，且 failed 集合里至少有一项已知违规 check。
    """

    def test_golden_case_passes(self, golden_run: dict) -> None:
        """构造与 eval_cases.json 正例相同的期望，打分结果应 passed=True。"""
        case = {
            "id": "golden-loop-ok",
            "expected_tools": ["todo", "web_search"],
            "forbidden_tools": ["execute_code"],
            "max_steps": 10,
            "allowed_exits": ["completed", "budget_grace_call"],
            "require_final_text": True,
        }
        score = score_case(case, golden_run)
        assert score.passed, [c for c in score.checks if not c.ok]

    def test_failure_case_fails_and_surfaces_checks(self, failure_run: dict) -> None:
        """负例打分应 passed=False；失败项应落在工具/role/cache/预算等已知 check 名上。"""
        case = {
            "id": "failure-wrong-tool-cache-break",
            "expected_tools": ["todo", "web_search"],
            "forbidden_tools": ["execute_code"],
            "max_steps": 4,
            "allowed_exits": ["completed", "budget_grace_call"],
            "require_final_text": True,
        }
        score = score_case(case, failure_run)
        assert not score.passed
        failed = {c.name for c in score.checks if not c.ok}
        # 至少命中下列违规类型之一（具体集合可随负例 fixture 调整）
        assert failed & {
            "no_forbidden",
            "tools_subset",
            "role_alternation",
            "system_stable",
            "tools_frozen",
            "exit",
            "final_text",
            "budget_consistent",
        }
