#!/usr/bin/env python3
"""Post-tool-use static-check hook.

Reads the Claude Code hook JSON from stdin. After a file edit/write:
  - Python files under app/backend  -> ruff check (lint)
  - TS/TSX files under app/frontend -> tsc --noEmit (typecheck; this brownfield
    app ships no ESLint config, so `next lint` would prompt interactively)
Prints the result and ALWAYS exits 0 (advisory — surfaces issues, never blocks).

Binaries are resolved via shutil.which so it works under Windows cmd.exe too
(npm/npx are .cmd shims that bare subprocess can't find without the extension).

Wired to: PostToolUse / Edit|Write|MultiEdit
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _emit(result: subprocess.CompletedProcess, ok: str, bad: str) -> None:
    if result.stdout.strip():
        print(result.stdout)
    if result.stderr.strip():
        print(result.stderr, file=sys.stderr)
    print(f"[lint-hook] {ok}" if result.returncode == 0 else f"[lint-hook] {bad}")


def main() -> None:
    try:
        data: dict = json.load(sys.stdin)
    except Exception as e:
        print(f"[lint-hook] Could not parse hook JSON: {e}", file=sys.stderr)
        sys.exit(0)

    tool_input: dict = data.get("tool_input") or {}
    file_path_raw = tool_input.get("file_path")
    if not file_path_raw:
        sys.exit(0)

    file_path = Path(file_path_raw).resolve()
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
    app_backend = project_dir / "app" / "backend"
    app_frontend = project_dir / "app" / "frontend"

    try:
        rel_str = file_path.relative_to(project_dir).as_posix()
    except ValueError:
        sys.exit(0)

    if rel_str.startswith("app/backend/") and file_path.suffix == ".py":
        uv_bin = shutil.which("uv") or "uv"
        print(f"[lint-hook] ruff check on {rel_str}")
        result = subprocess.run(
            [uv_bin, "run", "ruff", "check", str(file_path)],
            cwd=str(app_backend), capture_output=True, text=True,
        )
        _emit(result, ok="ruff: OK", bad="ruff: issues found (see above) — fix before committing")

    elif rel_str.startswith("app/frontend/") and file_path.suffix in (".ts", ".tsx"):
        npx_bin = shutil.which("npx")
        if not npx_bin:
            print("[lint-hook] npx not found on PATH; skipping frontend check")
            sys.exit(0)
        print(f"[lint-hook] tsc --noEmit (typecheck) triggered by {rel_str}")
        result = subprocess.run(
            [npx_bin, "tsc", "--noEmit"],
            cwd=str(app_frontend), capture_output=True, text=True,
        )
        _emit(result, ok="tsc: OK", bad="tsc: type errors found (see above) — fix before committing")

    sys.exit(0)  # advisory hook — never blocks


if __name__ == "__main__":
    main()
