#!/usr/bin/env python3
"""ralph/ralph.py - The Ralph loop (Python driver).

Cross-platform alternative to ralph.sh. Feeds PROMPT.md to a fresh headless
Claude CLI process each iteration until DONE.txt appears or MAX_ITER is reached.

Two modes:

  In-place (default):
      cd harness-engineering-demo
      python ralph/ralph.py
  Runs the loop on the CURRENTLY checked-out branch in this directory. Simple,
  but it commits onto whatever branch you are on - so only do this in a sandbox.

  Self-isolating worktree (opt-in):
      python ralph/ralph.py --worktree
      RALPH_WORKTREE=1 python ralph/ralph.py
  Ralph creates its OWN git worktree on a fresh branch, runs the whole loop
  inside it, and commits there. Your main working tree never moves. This is the
  unit you scale horizontally: launch several `--worktree` runs at once and each
  is an isolated agent on its own branch (see --db-isolate for the shared-DB
  caveat, and ralph/README.md for the full parallel pattern).

Env / flags:
    --worktree            | RALPH_WORKTREE=1       run inside a fresh worktree+branch
    --branch <name>       | RALPH_BRANCH=<name>    branch name (default ralph/run-<ts>)
    --db-isolate          | RALPH_DB_ISOLATE=1     give the run its own Postgres DB
    --cleanup             | RALPH_CLEANUP=1        remove the worktree on success (keep branch)
                            RALPH_WORKTREE_DIR     base dir for worktrees (default ../ralph-worktrees)
                            RALPH_MAX_ITER=15      hard iteration cap
                            RALPH_ITER_TIMEOUT=1800 per-iteration timeout (s)
                            RALPH_CLAUDE_BIN       override the claude binary (used by tests)

Requirements:
    - `claude` CLI on PATH (or RALPH_CLAUDE_BIN)
    - run from the repo root (where CLAUDE.md lives)
    - --db-isolate additionally needs the Postgres container up (app/docker-compose.yml)
      and `uv` for alembic.

WARNING: --dangerously-skip-permissions bypasses file-write confirmations.
Use only in a sandbox / dedicated worktree (which --worktree gives you).

NOTE (2026-06-15): `claude -p` draws from a separate Agent SDK credit pool,
distinct from your interactive Claude Code subscription.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()

MAX_ITER: int = int(os.environ.get("RALPH_MAX_ITER", "15"))
ITER_TIMEOUT: int = int(os.environ.get("RALPH_ITER_TIMEOUT", "1800"))  # seconds

# Set once we know where the loop actually runs (repo root, or a worktree).
LOG_FILE: Path = REPO_ROOT / "ralph" / "ralph.log"


def _ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg: str) -> None:
    line = f"[{_ts()}] {msg}"
    print(line, flush=True)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def _bin(name: str, override: str | None = None) -> str:
    """Resolve a binary, Windows-safe (.cmd shims). Optional env override."""
    return override or shutil.which(name) or name


def parse_config() -> dict:
    argv = sys.argv[1:]

    def flag(name: str, env: str) -> bool:
        return (name in argv) or os.environ.get(env, "").lower() in ("1", "true", "yes")

    def opt(name: str, env: str, default: str | None) -> str | None:
        if name in argv:
            i = argv.index(name)
            if i + 1 < len(argv):
                return argv[i + 1]
        return os.environ.get(env, default)

    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return {
        "worktree": flag("--worktree", "RALPH_WORKTREE"),
        "branch": opt("--branch", "RALPH_BRANCH", f"ralph/run-{ts}"),
        "db_isolate": flag("--db-isolate", "RALPH_DB_ISOLATE"),
        "cleanup": flag("--cleanup", "RALPH_CLEANUP"),
        "wt_base": Path(os.environ.get("RALPH_WORKTREE_DIR", str(REPO_ROOT.parent / "ralph-worktrees"))),
        "claude_bin": os.environ.get("RALPH_CLAUDE_BIN"),
    }


def create_worktree(branch: str, wt_base: Path) -> Path:
    """git worktree add a fresh branch; return the worktree path."""
    wt_base.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", branch).strip("-")
    wt_path = wt_base / slug
    if wt_path.exists():
        wt_path = wt_base / f"{slug}-{datetime.datetime.now().strftime('%H%M%S')}"
    git = _bin("git")
    r = subprocess.run(
        [git, "worktree", "add", str(wt_path), "-b", branch],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git worktree add failed: {(r.stderr or r.stdout).strip()}")
    return wt_path


def setup_isolated_db(work_root: Path, branch: str, env: dict) -> tuple[dict, str | None]:
    """Create a per-run Postgres DB and point DATABASE_URL at it. Best-effort.

    Each parallel worktree should get its own database so concurrent test runs
    do not stomp on each other's rows. We reuse the single Postgres container and
    just create a uniquely named database inside it.
    """
    db_name = "schedulr_ralph_" + (re.sub(r"[^a-z0-9]+", "_", branch.lower()).strip("_") or "run")
    docker = _bin("docker")
    # Target the container by its explicit name (docker-compose.yml: container_name:
    # schedulr-db). `docker compose exec` can fail to resolve the service when the
    # container was started under a different compose project; `docker exec` does not.
    create = subprocess.run(
        [docker, "exec", "-i", "schedulr-db",
         "psql", "-U", "schedulr", "-d", "postgres", "-c", f'CREATE DATABASE "{db_name}"'],
        capture_output=True, text=True,
    )
    blob = (create.stderr or "") + (create.stdout or "")
    if create.returncode != 0 and "already exists" not in blob:
        log(f"[db-isolate] could not create DB '{db_name}' ({blob.strip()[:160]}); using the shared DB. "
            "Parallel runs will collide.")
        return env, None

    env = dict(env)
    env["DATABASE_URL"] = f"postgresql+psycopg://schedulr:schedulr@localhost:5433/{db_name}"
    uv = _bin("uv")
    mig = subprocess.run(
        [uv, "run", "alembic", "upgrade", "head"],
        cwd=str(work_root / "app" / "backend"), env=env, capture_output=True, text=True,
    )
    if mig.returncode != 0:
        log(f"[db-isolate] alembic upgrade failed on '{db_name}': {(mig.stderr or mig.stdout).strip()[:160]}")
    else:
        log(f"[db-isolate] isolated database '{db_name}' created and migrated.")
    return env, db_name


def git_commit(work_root: Path, iteration: int) -> None:
    git = _bin("git")
    subprocess.run([git, "add", "-A"], cwd=str(work_root), check=False)
    diff = subprocess.run([git, "diff", "--cached", "--quiet"], cwd=str(work_root))
    if diff.returncode != 0:
        ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        subprocess.run(
            [git, "commit", "-m", f"ralph: iteration {iteration} - {ts}", "--no-verify"],
            cwd=str(work_root), check=False,
        )
        log(f"git commit: iteration {iteration}")
    else:
        log("git: nothing to commit this iteration")


def run_claude(spec: str, work_root: Path, claude_bin: str | None, env: dict) -> dict:
    """Invoke `claude -p` with the spec on stdin inside work_root."""
    claude = _bin("claude", claude_bin)
    result = subprocess.run(
        [claude, "-p", "--output-format", "json",
         "--dangerously-skip-permissions", "--max-turns", "40"],
        input=spec, capture_output=True, text=True, encoding="utf-8",
        timeout=ITER_TIMEOUT, cwd=str(work_root), env=env,
    )
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(result.stdout or "")
        if result.stderr:
            f.write(result.stderr)
    try:
        return json.loads(result.stdout) if (result.stdout or "").strip() else {}
    except json.JSONDecodeError:
        return {"raw": result.stdout}


def summary(cfg: dict, work_root: Path, branch: str, db_name: str | None, done: bool) -> None:
    if not cfg["worktree"]:
        return
    print("\n" + "=" * 64)
    print("Ralph worktree run summary")
    print("=" * 64)
    print(f"  Result:   {'DONE (spec complete)' if done else 'stopped (cap/timeout reached)'}")
    print(f"  Branch:   {branch}")
    print(f"  Worktree: {work_root}")
    print(f"  Log:      {LOG_FILE}")
    print(f"  Database: {db_name or 'shared (schedulr) - not isolated'}")
    print("  Review:   git -C \"%s\" log --oneline" % work_root)
    print("            git -C \"%s\" diff %s..%s" % (REPO_ROOT, _default_base(), branch))
    print("  Merge:    git -C \"%s\" merge %s   (or open a PR from the branch)" % (REPO_ROOT, branch))
    print("  Discard:  git -C \"%s\" worktree remove \"%s\" --force && git -C \"%s\" branch -D %s"
          % (REPO_ROOT, work_root, REPO_ROOT, branch))
    print("=" * 64)


def _default_base() -> str:
    git = _bin("git")
    r = subprocess.run([git, "symbolic-ref", "--short", "HEAD"], cwd=str(REPO_ROOT),
                       capture_output=True, text=True)
    return (r.stdout.strip() or "main")


def main() -> None:
    global LOG_FILE
    cfg = parse_config()
    branch = cfg["branch"]
    env = os.environ.copy()
    db_name: str | None = None

    # Decide where the loop runs.
    if cfg["worktree"]:
        try:
            work_root = create_worktree(branch, cfg["wt_base"])
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)
        LOG_FILE = work_root / "ralph" / "ralph.log"
        log(f"=== worktree mode: branch '{branch}' at {work_root} ===")
        if cfg["db_isolate"]:
            env, db_name = setup_isolated_db(work_root, branch, env)
    else:
        work_root = REPO_ROOT
        LOG_FILE = REPO_ROOT / "ralph" / "ralph.log"

    prompt_file = work_root / "ralph" / "PROMPT.md"
    done_file = work_root / "ralph" / "DONE.txt"

    if not prompt_file.exists():
        print(f"ERROR: PROMPT.md not found at {prompt_file}", file=sys.stderr)
        sys.exit(1)
    spec = prompt_file.read_text(encoding="utf-8")

    log("=== Ralph loop started ===")
    log(f"PROMPT: {prompt_file}")
    log(f"MAX_ITER: {MAX_ITER} | TIMEOUT per iter: {ITER_TIMEOUT}s")

    done = False
    for iteration in range(1, MAX_ITER + 1):
        log(f"--- Iteration {iteration} / {MAX_ITER} ---")
        if done_file.exists():
            log(f"DONE.txt found - spec complete after {iteration - 1} iterations.")
            done = True
            break
        try:
            run_claude(spec, work_root, cfg["claude_bin"], env)
            log(f"Claude finished iteration {iteration}")
        except subprocess.TimeoutExpired:
            log(f"Iteration {iteration} timed out after {ITER_TIMEOUT}s")
        except Exception as exc:
            log(f"Iteration {iteration} error: {exc}")

        git_commit(work_root, iteration)

        if done_file.exists():
            log(f"DONE.txt found - spec complete after {iteration} iterations.")
            done = True
            break
        log(f"Iteration {iteration} complete - spec not yet done.")

    if not done:
        log(f"MAX_ITER ({MAX_ITER}) reached without DONE.txt. Review ralph.log and fix_plan.md.")

    # Optional cleanup of the worktree (the branch is kept so work is never lost).
    if cfg["worktree"] and cfg["cleanup"] and done:
        git = _bin("git")
        subprocess.run([git, "worktree", "remove", str(work_root), "--force"],
                       cwd=str(REPO_ROOT), check=False)
        log(f"cleanup: removed worktree {work_root} (branch '{branch}' kept)")
        LOG_FILE = REPO_ROOT / "ralph" / "ralph.log"

    summary(cfg, work_root, branch, db_name, done)
    sys.exit(0 if done else 1)


if __name__ == "__main__":
    main()
