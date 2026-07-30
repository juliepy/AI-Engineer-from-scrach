"""离线评测打分器。

对照 notes/03_eval_harness.md — 断言关系，不冻结金标全文。
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from checkers import (
    check_budget_consistent,
    check_role_alternation,
    check_system_stable,
    check_tools_frozen,
)


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


@dataclass
class CaseScore:
    case_id: str
    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    tool_sequence: list[str] = field(default_factory=list)
    exit_reason: str | None = None
    api_calls: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "passed": self.passed,
            "exit_reason": self.exit_reason,
            "api_calls": self.api_calls,
            "tool_sequence": self.tool_sequence,
            "checks": [asdict(c) for c in self.checks],
        }


def tool_sequence_from_trace(trace: list[dict[str, Any]]) -> list[str]:
    seq: list[str] = []
    for ev in trace:
        if ev.get("kind") != "api_response":
            continue
        for tc in ev.get("tool_calls") or []:
            name = tc.get("name")
            if name:
                seq.append(name)
    return seq


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path: Path) -> list[dict[str, Any]]:
    """加载评测集：支持缩进 JSON 数组（.json）或 JSONL（.jsonl）。"""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix == ".json" or text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError(f"eval cases JSON 必须是数组: {path}")
        return data
    cases: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        cases.append(json.loads(line))
    return cases


def cases_to_jsonl(cases: list[dict[str, Any]]) -> str:
    header = (
        "# 人读请看 eval_cases.md；编辑请改 eval_cases.json。"
        "本文件由 run_eval_suite.py 从 .json 同步。\n"
    )
    body = "\n".join(json.dumps(c, ensure_ascii=False) for c in cases)
    return header + body + "\n"


def format_cases_table_md(cases: list[dict[str, Any]]) -> str:
    """人类可读总表（导出 / 控制台对照用）。"""
    lines = [
        "# Eval Cases",
        "",
        "| id | fixture | expected_tools | forbidden | max_steps | allowed_exits | final_text | notes |",
        "|----|---------|----------------|-----------|-----------|---------------|------------|-------|",
    ]
    for c in cases:
        exp = ", ".join(c.get("expected_tools") or []) or "—"
        forb = ", ".join(c.get("forbidden_tools") or []) or "—"
        exits = ", ".join(c.get("allowed_exits") or [])
        final = "yes" if c.get("require_final_text", True) else "no"
        notes = (c.get("notes") or "").replace("|", "\\|")
        lines.append(
            f"| `{c.get('id')}` | `{c.get('run_fixture')}` | {exp} | {forb} | "
            f"{c.get('max_steps')} | {exits} | {final} | {notes} |"
        )
    lines.append("")
    return "\n".join(lines)


def score_case(case: dict[str, Any], run: dict[str, Any]) -> CaseScore:
    trace = run.get("trace") or []
    messages = run.get("messages") or []
    actual_tools = tool_sequence_from_trace(trace)
    expected = set(case.get("expected_tools") or [])
    forbidden = set(case.get("forbidden_tools") or [])
    allowed_exits = set(case.get("allowed_exits") or ["completed"])
    max_steps = int(case.get("max_steps", 90))
    require_final = bool(case.get("require_final_text", True))

    checks: list[CheckResult] = []

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append(CheckResult(name=name, ok=ok, detail=detail))

    missing = expected - set(actual_tools)
    add(
        "tools_subset",
        not missing,
        "ok" if not missing else f"missing expected tools: {sorted(missing)}",
    )
    hit_forbidden = set(actual_tools) & forbidden
    add(
        "no_forbidden",
        not hit_forbidden,
        "ok" if not hit_forbidden else f"forbidden used: {sorted(hit_forbidden)}",
    )

    api_calls = int(run.get("api_calls", 0))
    add("steps", api_calls <= max_steps, f"api_calls={api_calls} max_steps={max_steps}")

    exit_reason = run.get("exit_reason")
    add(
        "exit",
        exit_reason in allowed_exits,
        f"exit_reason={exit_reason!r} allowed={sorted(allowed_exits)}",
    )

    final = (run.get("final_response") or "").strip()
    add(
        "final_text",
        (bool(final) if require_final else True),
        "ok" if final or not require_final else "empty final_response",
    )

    ok, detail = check_role_alternation(messages)
    add("role_alternation", ok, detail)
    ok, detail = check_system_stable(trace)
    add("system_stable", ok, detail)
    ok, detail = check_tools_frozen(trace)
    add("tools_frozen", ok, detail)
    ok, detail = check_budget_consistent(run)
    add("budget_consistent", ok, detail)

    return CaseScore(
        case_id=case["id"],
        passed=all(c.ok for c in checks),
        checks=checks,
        tool_sequence=actual_tools,
        exit_reason=exit_reason,
        api_calls=api_calls,
    )


from load_agent_loop_export import is_agent_loop_export_dir, load_agent_loop_export


def load_run(path: Path) -> dict[str, Any]:
    """加载单条 run：JSON fixture 或 02-run-agent exports 目录。"""
    path = path.resolve()
    if is_agent_loop_export_dir(path):
        return load_agent_loop_export(path)
    if path.is_file() and path.suffix == ".json":
        return load_json(path)
    raise FileNotFoundError(
        f"run_fixture 不是 JSON 也不是 02 export 目录: {path}"
    )


def score_suite(
    cases: list[dict[str, Any]],
    fixtures_dir: Path,
) -> list[CaseScore]:
    scores: list[CaseScore] = []
    for case in cases:
        run_path = (fixtures_dir / case["run_fixture"]).resolve()
        run = load_run(run_path)
        scores.append(score_case(case, run))
    return scores
