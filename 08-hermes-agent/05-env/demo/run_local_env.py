#!/usr/bin/env python3
"""Run real Hermes LocalEnvironment — no source edits.

Uses the full hermes-agent checkout on PYTHONPATH (same code as production).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEMO_ROOT = Path(__file__).resolve().parent
EXPORTS = DEMO_ROOT / "exports" / "local_env"
MODULE_ROOT = DEMO_ROOT.parent  # 05-env/


def _resolve_hermes_agent_root() -> Path:
    """Prefer HERMES_AGENT_ROOT; else sibling checkout next to AI_coding_interview."""
    env = os.environ.get("HERMES_AGENT_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / "tools" / "environments" / "local.py").is_file():
            return p
        raise SystemExit(f"HERMES_AGENT_ROOT={p} missing tools/environments/local.py")

    # demo → 05-env → 08-hermes-agent → AI_coding_interview → 人工智能面试题/hermes-agent
    candidates = [
        MODULE_ROOT.parents[2] / "hermes-agent",  # …/人工智能面试题/hermes-agent
        MODULE_ROOT.parents[1] / "hermes-agent",
        Path.home() / "hermes-agent",
    ]
    for c in candidates:
        if (c / "tools" / "environments" / "local.py").is_file():
            return c.resolve()
    raise SystemExit(
        "Cannot find hermes-agent. Set HERMES_AGENT_ROOT to the repo root "
        "(directory that contains tools/environments/local.py)."
    )


def main() -> int:
    root = _resolve_hermes_agent_root()
    sys.path.insert(0, str(root))

    # Import AFTER path setup — real source, unmodified
    from tools.environments.local import LocalEnvironment

    cwd = str(DEMO_ROOT)
    env = LocalEnvironment(cwd=cwd, timeout=30)
    commands = [
        "echo hermes-env-ok",
        "pwd",
        "echo HOME=$HOME",
        "true",
    ]
    rows = []
    try:
        for cmd in commands:
            result = env.execute(cmd)
            rows.append(
                {
                    "command": cmd,
                    "returncode": result.get("returncode"),
                    "output": (result.get("output") or "").rstrip("\n"),
                    "cwd_after": env.cwd,
                }
            )
            print(f"$ {cmd}")
            print(f"  rc={result.get('returncode')}  out={rows[-1]['output']!r}")
            print(f"  cwd={env.cwd}")
    finally:
        env.cleanup()

    EXPORTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hermes_agent_root": str(root),
        "backend": "LocalEnvironment",
        "source": "tools/environments/local.py (unmodified)",
        "cwd_start": cwd,
        "probes": rows,
    }
    (EXPORTS / "00_raw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# LocalEnvironment demo",
        "",
        f"- hermes_agent_root: `{root}`",
        f"- source: `tools/environments/local.py` (unmodified)",
        f"- generated: {payload['generated_at']}",
        "",
        "## Probes",
        "",
        "| command | rc | output | cwd_after |",
        "|---------|----|--------|-----------|",
    ]
    for r in rows:
        out = r["output"].replace("|", "\\|").replace("\n", "\\n")
        lines.append(
            f"| `{r['command']}` | {r['returncode']} | `{out[:120]}` | `{r['cwd_after']}` |"
        )
    lines += [
        "",
        "## Call flow",
        "",
        "```text",
        "LocalEnvironment(cwd)",
        "  └─ init_session()          # BaseEnvironment",
        "execute(cmd)",
        "  ├─ _wrap_command()         # source snapshot → cd → eval → CWD marker",
        "  ├─ _run_bash()             # local.py · Popen(bash -c)",
        "  ├─ _wait_for_process()     # base.py",
        "  └─ _update_cwd()",
        "```",
        "",
    ]
    (EXPORTS / "01_report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {EXPORTS}")
    return 0 if all(r["returncode"] == 0 for r in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
