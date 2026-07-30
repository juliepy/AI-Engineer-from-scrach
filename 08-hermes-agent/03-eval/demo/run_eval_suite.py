#!/usr/bin/env python3
# =============================================================================
# Eval + Trace Demo — pytest 契约（近 Hermes）+ 离线打分 / RCA（教学报告）
# =============================================================================
# 对照讲稿: notes/01_eval_invariants.md · 02_logging_trace.md · 03_eval_harness.md
#
# 两层（勿混为一谈）:
#   A. pytest contracts  ≈ Hermes CI（tests/agent/* 风格，测关系不测快照）
#   B. score_suite + RCA ≈ 面试用 Trace 报告层（真仓无此 JSONL harness）
#
# 跑法（无需 API Key）:
#   cd 03-eval/demo
#   pip install -r requirements.txt   # pytest
#   python run_eval_suite.py
# =============================================================================
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
for _subdir in ("invariants", "logging", "harness"):
    sys.path.insert(0, str(HERE / "teaching" / _subdir))

from checkers import CHANGE_DETECTOR_ANTI_PATTERNS  # noqa: E402
from rca import analyze_failure, format_rca_md  # noqa: E402
from scorer import (  # noqa: E402
    cases_to_jsonl,
    format_cases_table_md,
    load_cases,
    load_run,
    score_suite,
)
from session_logger import demo_emit_session_logs, filter_log_by_session  # noqa: E402

FIXTURES = HERE / "fixtures"
RUN_JSON = FIXTURES / "from_02_agent_loop.json"
FAILURE_JSON = FIXTURES / "failure_run.json"
CASES_JSON = FIXTURES / "eval_cases.json"
CASES_JSONL = FIXTURES / "eval_cases.jsonl"
EXPORT_DIR = HERE / "exports" / "eval_run"
CONTRACT_TEST = HERE / "teaching" / "invariants" / "test_agent_loop_contracts.py"
REAL_02_EXPORT = (HERE / "../../02-run-agent/demo/exports/agent_loop").resolve()


def resolve_cases_path() -> Path:
    if CASES_JSON.exists():
        return CASES_JSON
    raise FileNotFoundError(f"missing {CASES_JSON.name}")


def refresh_from_02_export() -> dict | None:
    """若存在 02 实跑导出，刷新 fixtures/from_02_agent_loop.json。"""
    if not (REAL_02_EXPORT / "06_trace.md").exists():
        return None
    converted = load_run(REAL_02_EXPORT)
    dump(
        RUN_JSON,
        json.dumps(converted, ensure_ascii=False, indent=2),
    )
    return converted


def banner(step: str, title: str) -> None:
    print()
    print("=" * 72)
    print(f"  STEP {step} · {title}")
    print("=" * 72)


def dump(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  wrote {path.relative_to(HERE)}")


def run_contract_pytest() -> tuple[bool, str]:
    """近 Hermes：先跑 pytest 契约，再写报告。"""
    cmd = [sys.executable, "-m", "pytest", str(CONTRACT_TEST), "-q", "--tb=line"]
    proc = subprocess.run(
        cmd,
        cwd=str(HERE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, out


def format_invariants_md(scores: list, pytest_ok: bool, pytest_out: str) -> str:
    lines = [
        "# Invariant Checks",
        "",
        "对照 AGENTS.md：断言关系，不冻结快照。",
        "",
        "## Layer A · pytest contracts（近 Hermes CI）",
        "",
        f"- result: `{'PASS' if pytest_ok else 'FAIL'}`",
        f"- file: `{CONTRACT_TEST.relative_to(HERE).as_posix()}`",
        "",
        "```text",
        pytest_out.rstrip() or "(no output)",
        "```",
        "",
        "## Anti-patterns（不要写）",
        "",
    ]
    for ap in CHANGE_DETECTOR_ANTI_PATTERNS:
        lines.append(f"- `{ap}`")
    lines += ["", "## Layer B · offline case scores", ""]
    for s in scores:
        mark = "PASS" if s.passed else "FAIL"
        lines.append(f"### `{s.case_id}` — {mark}")
        lines.append("")
        for c in s.checks:
            icon = "✓" if c.ok else "✗"
            lines.append(f"- {icon} `{c.name}`: {c.detail}")
        lines.append("")
    return "\n".join(lines)


def format_workflow_md(scores: list, session_id: str, pytest_ok: bool) -> str:
    passed = sum(1 for s in scores if s.passed)
    total = len(scores)
    lines = [
        "# Eval Suite Workflow",
        "",
        "```text",
        "Layer A  pytest teaching/invariants/test_agent_loop_contracts.py",
        "         （Hermes 风格：Test* 类 + 关系断言）",
        "      │",
        "Layer B  fixtures/eval_cases.json",
        "         + from_02_agent_loop.json（正例）",
        "         + failure_run.json（负例）",
        "      │",
        "      ▼",
        "score_suite()  →  tools / steps / exit / invariants",
        "      │",
        "      ├─ session_logger demo (session_tag)",
        "      └─ RCA on failing cases",
        "```",
        "",
        f"- pytest_contracts: `{'PASS' if pytest_ok else 'FAIL'}`",
        f"- offline cases: `{total}`",
        f"- offline passed: `{passed}`",
        f"- offline failed: `{total - passed}`",
        f"- session_demo: `{session_id}`",
        f"- offline: `true`（无 API Key）",
        "",
        "## Case summary",
        "",
        "| case | pass | exit | api_calls | tools |",
        "|------|------|------|-----------|-------|",
    ]
    for s in scores:
        tools = ",".join(s.tool_sequence[:6])
        if len(s.tool_sequence) > 6:
            tools += ",…"
        lines.append(
            f"| `{s.case_id}` | {s.passed} | `{s.exit_reason}` | {s.api_calls} | `{tools}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    banner("0", "Refresh from_02_agent_loop.json (if 02 export exists)")
    converted = refresh_from_02_export()
    if converted:
        print(f"  refreshed from {REAL_02_EXPORT}")
        print(
            f"  exit={converted.get('exit_reason')} "
            f"api_calls={converted.get('api_calls')} "
            f"budget={converted.get('budget_used')}/{converted.get('budget_max')}"
        )
        dump(
            EXPORT_DIR / "00_from_02_summary.md",
            "\n".join(
                [
                    "# from_02_agent_loop.json",
                    "",
                    f"- source: `{REAL_02_EXPORT}`",
                    f"- exit_reason: `{converted.get('exit_reason')}`",
                    f"- api_calls: `{converted.get('api_calls')}`",
                    f"- budget: `{converted.get('budget_used')}/{converted.get('budget_max')}`",
                    f"- messages: `{len(converted.get('messages') or [])}`",
                    f"- trace events: `{len(converted.get('trace') or [])}`",
                    "",
                ]
            ),
        )
    elif RUN_JSON.exists():
        print(f"  using existing {RUN_JSON.name}")
    else:
        raise FileNotFoundError(
            f"missing {RUN_JSON}; run 02-run-agent/demo first or place the JSON under fixtures/"
        )
    if not FAILURE_JSON.exists():
        raise FileNotFoundError(f"missing {FAILURE_JSON}")

    banner("1", "Layer A · pytest contracts (Hermes-like)")
    pytest_ok, pytest_out = run_contract_pytest()
    print(pytest_out.rstrip() or "  (no pytest output)")
    if not pytest_ok:
        print("  WARNING: pytest contracts failed — continue to offline reports")

    banner("2", "Layer B · offline score (golden + failure)")
    cases_path = resolve_cases_path()
    cases = load_cases(cases_path)
    print(f"  cases: {len(cases)} from {cases_path.name}")
    dump(CASES_JSONL, cases_to_jsonl(cases))
    dump(EXPORT_DIR / "00_cases.md", format_cases_table_md(cases))
    for c in cases:
        print(
            f"  · {c['id']:36}  fixture={c.get('run_fixture')}  "
            f"max_steps={c.get('max_steps')}"
        )

    scores = score_suite(cases, FIXTURES)
    for s in scores:
        mark = "PASS" if s.passed else "FAIL"
        print(f"  [{mark}] {s.case_id}  exit={s.exit_reason}  tools={s.tool_sequence}")

    scores_json = [s.to_dict() for s in scores]
    dump(EXPORT_DIR / "01_case_scores.json", json.dumps(scores_json, ensure_ascii=False, indent=2))
    dump(EXPORT_DIR / "02_invariants.md", format_invariants_md(scores, pytest_ok, pytest_out))

    banner("3", "Session-tagged logging demo")
    session_id = "sess_eval_demo"
    captured = demo_emit_session_logs(session_id)
    agent_log = captured.agent_text()
    errors_log = captured.errors_text()
    dump(
        EXPORT_DIR / "04_session_log_slice.md",
        "\n".join(
            [
                "# Session Log Slice",
                "",
                f"session_id: `{session_id}`",
                "",
                "## Live emit (teaching logger)",
                "",
                "```text",
                agent_log.rstrip(),
                "```",
                "",
                "## errors.log (WARNING+)",
                "",
                "```text",
                errors_log.rstrip(),
                "```",
                "",
                "## component=agent",
                "",
                "```text",
                captured.component_text("agent").rstrip(),
                "```",
                "",
                "## Filter live agent log by session",
                "",
                "```text",
                "\n".join(filter_log_by_session(agent_log, session_id)),
                "```",
                "",
            ]
        ),
    )
    print(f"  session_tag lines: {len(filter_log_by_session(agent_log, session_id))}")

    banner("4", "RCA on failing cases")
    rca_parts: list[str] = ["# Trace RCA Reports", ""]
    case_by_id = {c["id"]: c for c in cases}
    failed_n = 0
    for s in scores:
        if s.passed:
            continue
        failed_n += 1
        case = case_by_id[s.case_id]
        run = load_run((FIXTURES / case["run_fixture"]).resolve())
        report = analyze_failure(case, run, s)
        rca_parts.append(format_rca_md(report))
        rca_parts.append("\n---\n")
        print(f"  RCA {s.case_id}: root_cause={report['root_cause']}")
    if failed_n == 0:
        rca_parts.append("_All cases passed — no RCA._\n")
        print("  (all passed)")
    dump(EXPORT_DIR / "03_trace_rca.md", "\n".join(rca_parts))

    dump(EXPORT_DIR / "00_workflow.md", format_workflow_md(scores, session_id, pytest_ok))

    banner("5", "Done")
    passed = sum(1 for s in scores if s.passed)
    print(f"  pytest: {'PASS' if pytest_ok else 'FAIL'}")
    print(f"  offline: {passed}/{len(scores)} cases passed (failure case should FAIL)")
    print(f"  golden: {RUN_JSON.relative_to(HERE)}")
    print(f"  failure: {FAILURE_JSON.relative_to(HERE)}")
    print(f"  exports → {EXPORT_DIR.relative_to(HERE)}")
    # pytest 失败则非零；离线负例 FAIL 是预期，不据此失败
    return 0 if pytest_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
