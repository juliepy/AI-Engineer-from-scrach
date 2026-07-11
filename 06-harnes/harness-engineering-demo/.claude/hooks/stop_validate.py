#!/usr/bin/env python3
"""Stop hook — validation gate.

Reads Claude Code's Stop hook JSON from stdin. If stop_hook_active is True
(meaning this hook already triggered a block and Claude is being asked whether
to continue), exits 0 immediately to prevent an infinite loop.

Otherwise runs the backend validation gate (ruff + pytest). On failure, prints
a JSON block decision that blocks the stop and tells Claude to fix the issues.
On pass, exits 0 silently.

Wired to: Stop
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str) -> tuple[bool, str]:
    """Run a command; return (passed, summary_text)."""
    exe = shutil.which(cmd[0]) or cmd[0]
    result = subprocess.run([exe, *cmd[1:]], cwd=cwd, capture_output=True, text=True)
    passed = result.returncode == 0
    out = (result.stdout + result.stderr).strip()
    # Keep summary short for the block reason
    lines = [l for l in out.splitlines() if l.strip()]
    summary = "\n".join(lines[:20]) if lines else "(no output)"
    return passed, summary


def main() -> None:
    try:
        data: dict = json.load(sys.stdin)
    except Exception as e:
        # If we can't parse stdin, fail open (don't block)
        print(f"[stop-hook] Could not parse hook JSON: {e}", file=sys.stderr)
        sys.exit(0)

    # Prevent infinite loop: if the hook is already active from a prior block, pass through
    if data.get("stop_hook_active"):
        sys.exit(0)

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    backend_dir = str(project_dir / "app" / "backend")

    failures: list[str] = []

    # --- ruff ---
    passed, summary = run(["uv", "run", "ruff", "check", "app"], backend_dir)
    if not passed:
        failures.append(f"ruff check failed:\n{summary}")

    # --- pytest ---
    passed, summary = run(["uv", "run", "pytest", "-q", "--tb=short"], backend_dir)
    if not passed:
        failures.append(f"pytest failed:\n{summary}")

    if failures:
        reason = "Validation failed: " + " | ".join(
            f.replace("\n", " ") for f in failures
        )
        reason += ". Fix the issues and re-run."
        block = {"decision": "block", "reason": reason}
        print(json.dumps(block))
        sys.exit(0)

    # All green — allow stop
    sys.exit(0)


if __name__ == "__main__":
    main()
