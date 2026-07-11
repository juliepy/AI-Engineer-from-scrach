#!/usr/bin/env python3
"""PreToolUse security guard.

Denies two classes of dangerous operations BEFORE any tool runs:

  1. Reading, editing, or writing a real `.env` file (it holds secrets),
     across every vector a coding agent might try:
       - the Read / Edit / Write / MultiEdit / NotebookEdit tools (file_path),
       - Bash commands (cat, grep, sed, awk, less, xxd, base64, strings,
         `python -c "open('.env')"`, `source .env`, `cp .env ...`,
         `find ... -exec cat`, obfuscated globs like `.e*` / `.??v`, etc.),
       - Glob / Grep file targeting (pattern / path / glob).
     Template files (.env.example/.sample/.template/.dist/.defaults) stay
     ALLOWED so the agent can still scaffold non-secret config.

  2. Recursive directory deletion via Bash: `rm -r`/`-rf`/`-fr`/`-Rf`,
     `rmdir`, `find ... -delete`, `find ... -exec rm`, `git clean -d`.

Blocking uses the PreToolUse decision schema (permissionDecision: "deny")
printed to stdout with exit 0, so Claude gets the reason and can adapt.
On any parse/internal error the hook fails OPEN (exit 0) so a malformed
event can never brick the session.

Note: PreToolUse hooks still fire under `--dangerously-skip-permissions`
and headless `claude -p`, so this guard holds even in unattended Ralph runs.

Wired to (PreToolUse): Bash|Read|Edit|Write|MultiEdit|NotebookEdit|Glob|Grep
"""
import json
import re
import sys

# Template env files that carry no secrets and stay readable/writable.
ENV_ALLOWED = {
    ".env.example",
    ".env.sample",
    ".env.template",
    ".env.dist",
    ".env.defaults",
}

# A `.env` reference in free text: ".env", ".env.local", and the ".env" in
# "config.env". The optional group grabs a single ".suffix" (e.g. ".local").
ENV_TOKEN_RE = re.compile(r"\.env(?:\.[\w-]+)?", re.IGNORECASE)

# Obfuscated globs that are almost certainly reaching for a .env file.
ENV_GLOB_RE = re.compile(r"\.e(?:nv)?[\*\?]|\.\?\?v|\*\.env\b", re.IGNORECASE)

# Directory-deletion vectors (checked on whitespace-normalized command text).
RMDIR_RE = re.compile(r"\brmdir\b", re.IGNORECASE)
FIND_DELETE_RE = re.compile(r"\bfind\b[^|;&\n]*?(?:-delete\b|-exec\s+rm\b)", re.IGNORECASE)
GIT_CLEAN_DIR_RE = re.compile(r"\bgit\s+clean\b[^|;&\n]*-[a-z]*d", re.IGNORECASE)


def _clean(token: str) -> str:
    return token.strip().strip('"').strip("'")


def _basename(path: str) -> str:
    p = _clean(path).replace("\\", "/").rstrip("/")
    return p.rsplit("/", 1)[-1]


def _is_protected_env_name(name: str) -> bool:
    name = name.lower()
    if name in ENV_ALLOWED:
        return False
    return name == ".env" or name.startswith(".env.")


def _path_is_protected_env(path: str) -> bool:
    return bool(path) and _is_protected_env_name(_basename(path))


def _text_touches_protected_env(text: str) -> bool:
    """True if a shell command / glob references a non-template .env file."""
    if not text:
        return False
    if ENV_GLOB_RE.search(text):
        return True
    for m in ENV_TOKEN_RE.finditer(text):
        if m.group(0).lower() not in ENV_ALLOWED:
            return True
    return False


def _command_deletes_dir(cmd: str) -> bool:
    norm = re.sub(r"\s+", " ", cmd)
    if RMDIR_RE.search(norm) or FIND_DELETE_RE.search(norm) or GIT_CLEAN_DIR_RE.search(norm):
        return True
    # `rm` with a recursive flag in any form/order: -r, -R, -rf, -fr, --recursive
    for m in re.finditer(r"\brm\b([^|;&\n]*)", norm, re.IGNORECASE):
        args = m.group(1).lower()
        if "--recursive" in args:
            return True
        # any short-flag cluster (a leading single dash) that contains 'r'
        for flag in re.findall(r"(?<!\w)-[a-z]+", args):
            if not flag.startswith("--") and "r" in flag:
                return True
    return False


def _deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


ENV_HINT = "Reading/editing/copying/sourcing a .env is blocked by the project security hook. Use a .env.example template for non-secret config."


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparseable event: fail open, never brick the session

    tool = data.get("tool_name", "")
    ti = data.get("tool_input", {}) or {}

    try:
        if tool in ("Read", "Edit", "Write"):
            if _path_is_protected_env(ti.get("file_path", "")):
                _deny(f"Blocked: '{ti.get('file_path')}' is a protected .env file. {ENV_HINT}")

        elif tool == "MultiEdit":
            paths = [ti.get("file_path", "")]
            paths += [e.get("file_path", "") for e in ti.get("edits", []) if isinstance(e, dict)]
            for p in paths:
                if _path_is_protected_env(p):
                    _deny(f"Blocked: '{p}' is a protected .env file. {ENV_HINT}")

        elif tool == "NotebookEdit":
            if _path_is_protected_env(ti.get("notebook_path", "")):
                _deny(f"Blocked: editing a protected .env file. {ENV_HINT}")

        elif tool == "Glob":
            for c in (ti.get("pattern", ""), ti.get("path", "")):
                if _text_touches_protected_env(c) or _path_is_protected_env(c):
                    _deny(f"Blocked: globbing a protected .env file. {ENV_HINT}")

        elif tool == "Grep":
            # `pattern` is the content regex (don't inspect); guard the file targets.
            for c in (ti.get("path", ""), ti.get("glob", "")):
                if _text_touches_protected_env(c) or _path_is_protected_env(c):
                    _deny(f"Blocked: grepping a protected .env file leaks its contents. {ENV_HINT}")

        elif tool == "Bash":
            cmd = ti.get("command", "") or ""
            if _command_deletes_dir(cmd):
                _deny(
                    "Blocked: recursive directory deletion (rm -r/-rf, rmdir, "
                    "find -delete, find -exec rm, git clean -d) is denied by the "
                    "project security hook. Delete specific files explicitly instead."
                )
            if _text_touches_protected_env(cmd):
                _deny(f"Blocked: this command references a protected .env file. {ENV_HINT}")
    except Exception:
        sys.exit(0)  # internal error: fail open

    sys.exit(0)


if __name__ == "__main__":
    main()
