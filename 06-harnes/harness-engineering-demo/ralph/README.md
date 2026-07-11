# Ralph — Autonomous Spec-Driven Loop

Ralph is a tight feedback loop that re-feeds a spec (`PROMPT.md`) to a fresh headless Claude process each iteration until the spec is fully satisfied or a safety cap is hit.

## What it does

```
loop:
  1. Check for DONE.txt → exit if present
  2. cat PROMPT.md | claude -p --output-format json --dangerously-skip-permissions --max-turns 40
  3. git add -A && git commit  (captures each iteration's work)
  4. Check for DONE.txt again
  5. Repeat up to MAX_ITER times
```

Claude reads `PROMPT.md`, does one logical unit of work (per the spec's work pattern), runs the specified validation commands, and when all spec items pass it runs `touch ralph/DONE.txt` to signal completion.

## Files

| File | Purpose |
|------|---------|
| `ralph.sh` | Bash driver (Linux/macOS) |
| `ralph.py` | Python driver (cross-platform, Windows-safe) |
| `PROMPT.md` | The spec Claude receives every iteration |
| `ralph.log` | Append-only log of every iteration's output |
| `fix_plan.md` | Running log Claude maintains across iterations |

## Running

```bash
# From repo root — bash driver
bash ralph/ralph.sh

# Python driver (Windows / any platform)
python ralph/ralph.py

# Tune limits with env vars
RALPH_MAX_ITER=10 RALPH_ITER_TIMEOUT=900 python ralph/ralph.py
```

## Self-isolating worktree mode

By default Ralph runs in place and commits onto your current branch, so you have to remember to sandbox it. Pass `--worktree` (or `RALPH_WORKTREE=1`) and Ralph creates its OWN git worktree on a fresh branch, runs the whole loop there, and commits to that branch. Your main working tree never moves.

```bash
# Ralph spins up its own worktree + branch, runs there, prints a review summary
python ralph/ralph.py --worktree

# name the branch, and remove the worktree on success (the branch is kept)
python ralph/ralph.py --worktree --branch ralph/csv-export --cleanup
```

At the end it prints the branch, the worktree path, and the exact commands to review (`git diff main..<branch>`), merge, or discard the run.

| Flag / env | Effect |
|------------|--------|
| `--worktree` / `RALPH_WORKTREE=1` | run inside a fresh worktree + branch |
| `--branch <name>` / `RALPH_BRANCH` | branch name (default `ralph/run-<timestamp>`) |
| `--cleanup` / `RALPH_CLEANUP=1` | remove the worktree on success (branch kept) |
| `RALPH_WORKTREE_DIR` | where worktrees live (default `../ralph-worktrees`) |
| `--db-isolate` / `RALPH_DB_ISOLATE=1` | give the run its own Postgres database |
| `RALPH_CLAUDE_BIN` | override the `claude` binary (used by tests) |

## Scaling to parallel agents

The worktree is the unit you scale horizontally. Launch several `--worktree` runs at once and each is an isolated agent on its own branch and working copy, all sharing one `.git`:

```bash
python ralph/ralph.py --worktree --branch ralph/feature-a --db-isolate &
python ralph/ralph.py --worktree --branch ralph/feature-b --db-isolate &
python ralph/ralph.py --worktree --branch ralph/feature-c --db-isolate &
wait
# review each branch, then merge or open PRs
```

The one shared resource is the database. This app uses a single Postgres on host :5433, so parallel runs would otherwise stomp on each other's rows. `--db-isolate` solves it: per run it creates a uniquely named database (`schedulr_ralph_<branch>`) inside the same container, runs the migrations, and points that run's `DATABASE_URL` at it, so each agent's tests are isolated. (It needs the Postgres container up and `uv` available; if it can't create the database it logs a warning and falls back to the shared one.) Dependencies isolate on their own because `uv` venvs and `node_modules` live per worktree.

This is the concrete version of the "every ticket goes in, a pull request comes out, run many in parallel across worktrees" operating model.

## Guardrails

| Guardrail | Default | Purpose |
|-----------|---------|---------|
| `MAX_ITER` | 15 | Hard cap — prevents runaway loops |
| `ITER_TIMEOUT` | 1800 s | Per-iteration wall-clock limit |
| `DONE.txt` sentinel | — | Claude writes this only when ALL spec items pass |
| `git commit` per iter | — | Every iteration's changes are captured and reversible |

## `--dangerously-skip-permissions`

This flag tells Claude to skip interactive permission prompts for file writes, shell commands, etc. **Use only in a sandbox or dedicated worktree.** Never run Ralph on your main working branch.

## Agent SDK Credit Note (2026-06-15)

From 2026-06-15 onward, `claude -p` (headless / programmatic mode) draws from a **separate Agent SDK credit pool** rather than your interactive Claude Code subscription. Check your Anthropic console for Agent SDK usage and limits before running long Ralph loops.

## Anatomy of a Good PROMPT.md

1. **Goal** — one paragraph: what feature to build.
2. **Spec Items** — numbered checklist: each item is a concrete, verifiable condition.
3. **Work Pattern** — tell Claude to do ONE logical change per iteration, record in `fix_plan.md`, and only `touch DONE.txt` when all items pass.
4. **Fix Plan File** — instruct Claude to append `## Iteration N` entries with what changed, validation result, and what's next.

See `ralph/PROMPT.md` for the example (CSV export / SCH-142).
