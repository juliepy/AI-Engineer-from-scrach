"""对失败 run 做根因分析（教学版）。"""
from __future__ import annotations

from typing import Any

from scorer import CaseScore, tool_sequence_from_trace


def analyze_failure(case: dict[str, Any], run: dict[str, Any], score: CaseScore) -> dict[str, Any]:
    """根据失败 checks + trace 归纳 root_cause。"""
    failed = [c for c in score.checks if not c.ok]
    failed_names = {c.name for c in failed}
    evidence: list[str] = []
    hypotheses: list[str] = []

    for c in failed:
        evidence.append(f"{c.name}: {c.detail}")

    # 从 trace 抽关键 tool_calls
    for ev in run.get("trace") or []:
        if ev.get("kind") == "api_response" and ev.get("tool_calls"):
            names = [tc.get("name") for tc in ev["tool_calls"]]
            evidence.append(f"api#{ev.get('api_call')} tool_calls={names}")

    root = "unknown"
    if "no_forbidden" in failed_names or "tools_subset" in failed_names:
        root = "wrong_tool"
        hypotheses.append("模型选错工具或漏掉必要工具；对照 expected_tools / forbidden_tools")
    if "role_alternation" in failed_names:
        root = "context_corruption" if root == "unknown" else root + "+role_break"
        hypotheses.append("消息 role 交替被破坏（同 role 连发 / 中途插合成 user）→ 破 prompt cache 风险")
    if "system_stable" in failed_names or "tools_frozen" in failed_names:
        root = "cache_break" if root == "unknown" else root + "+cache_break"
        hypotheses.append("同 turn 内 system 或 tools schema 变化 → prompt cache 失效")
    if "exit" in failed_names or "budget_consistent" in failed_names:
        if root == "unknown":
            root = "budget_exhaustion"
        hypotheses.append("预算/退出理由异常：空转 tool 调用或未走 grace 收尾")
    if "steps" in failed_names:
        hypotheses.append("步数超 max_steps：循环未收敛")
    if "final_text" in failed_names:
        hypotheses.append("无最终文本：可能卡在 tool_calls 或 interrupt")

    return {
        "case_id": case["id"],
        "root_cause": root,
        "passed": score.passed,
        "exit_reason": run.get("exit_reason"),
        "api_calls": run.get("api_calls"),
        "tool_sequence": tool_sequence_from_trace(run.get("trace") or []),
        "failed_checks": [c.name for c in failed],
        "evidence": evidence,
        "fix_hypothesis": hypotheses,
        "notes": case.get("notes", ""),
    }


def format_rca_md(report: dict[str, Any]) -> str:
    lines = [
        "# Trace RCA",
        "",
        f"- case: `{report['case_id']}`",
        f"- root_cause: **{report['root_cause']}**",
        f"- exit_reason: `{report.get('exit_reason')}`",
        f"- api_calls: `{report.get('api_calls')}`",
        f"- tool_sequence: `{report.get('tool_sequence')}`",
        "",
        "## Failed checks",
        "",
    ]
    for name in report.get("failed_checks") or []:
        lines.append(f"- `{name}`")
    lines += ["", "## Evidence", ""]
    for e in report.get("evidence") or []:
        lines.append(f"- {e}")
    lines += ["", "## Fix hypothesis", ""]
    for h in report.get("fix_hypothesis") or []:
        lines.append(f"- {h}")
    if report.get("notes"):
        lines += ["", "## Case notes", "", report["notes"], ""]
    return "\n".join(lines)
