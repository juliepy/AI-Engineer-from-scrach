#!/usr/bin/env bash
# ralph/ralph.sh - The Ralph loop (bash driver)
#
# Feeds PROMPT.md to a fresh headless Claude each iteration until DONE.txt
# appears or MAX_ITER is reached.
#
# Two modes:
#   In-place (default):   bash ralph/ralph.sh
#       Runs on the currently checked-out branch in this directory.
#   Self-isolating:       bash ralph/ralph.sh --worktree
#       Ralph creates its OWN git worktree on a fresh branch and runs there;
#       your main working tree never moves. Launch several at once for parallel
#       isolated agents (see --db-isolate and ralph/README.md).
#
# Flags / env:
#   --worktree   | RALPH_WORKTREE=1        run inside a fresh worktree+branch
#   --branch X   | RALPH_BRANCH=X          branch name (default ralph/run-<ts>)
#   --db-isolate | RALPH_DB_ISOLATE=1      give the run its own Postgres DB
#   --cleanup    | RALPH_CLEANUP=1         remove the worktree on success (keep branch)
#                  RALPH_WORKTREE_DIR      base dir for worktrees (default ../ralph-worktrees)
#                  RALPH_MAX_ITER=15  RALPH_ITER_TIMEOUT=1800  RALPH_CLAUDE_BIN
#
# WARNING: --dangerously-skip-permissions bypasses file-write confirmations.
# Use only in a sandbox / dedicated worktree (which --worktree gives you).
#
# NOTE (2026-06-15): `claude -p` draws from a separate Agent SDK credit pool,
# distinct from your interactive Claude Code subscription.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

MAX_ITER="${RALPH_MAX_ITER:-15}"
ITER_TIMEOUT="${RALPH_ITER_TIMEOUT:-1800}"
CLAUDE_BIN="${RALPH_CLAUDE_BIN:-claude}"

# --- parse flags (env vars provide defaults) ---
WORKTREE="${RALPH_WORKTREE:-}"
DB_ISOLATE="${RALPH_DB_ISOLATE:-}"
CLEANUP="${RALPH_CLEANUP:-}"
BRANCH="${RALPH_BRANCH:-ralph/run-$(date +%Y%m%d-%H%M%S)}"
WT_BASE="${RALPH_WORKTREE_DIR:-$REPO_ROOT/../ralph-worktrees}"
while [ $# -gt 0 ]; do
    case "$1" in
        --worktree) WORKTREE=1 ;;
        --db-isolate) DB_ISOLATE=1 ;;
        --cleanup) CLEANUP=1 ;;
        --branch) shift; BRANCH="$1" ;;
        *) echo "unknown arg: $1" >&2 ;;
    esac
    shift
done

WORK_ROOT="$REPO_ROOT"
DB_NAME=""

if [ -n "$WORKTREE" ]; then
    SLUG="$(echo "$BRANCH" | tr -c 'A-Za-z0-9._-' '-' | sed 's/-*$//')"
    mkdir -p "$WT_BASE"
    WORK_ROOT="$WT_BASE/$SLUG"
    [ -e "$WORK_ROOT" ] && WORK_ROOT="$WT_BASE/$SLUG-$(date +%H%M%S)"
    git -C "$REPO_ROOT" worktree add "$WORK_ROOT" -b "$BRANCH"
    echo "=== worktree mode: branch '$BRANCH' at $WORK_ROOT ==="
fi

PROMPT_FILE="$WORK_ROOT/ralph/PROMPT.md"
DONE_FILE="$WORK_ROOT/ralph/DONE.txt"
LOG_FILE="$WORK_ROOT/ralph/ralph.log"

# --- optional per-run database isolation ---
if [ -n "$WORKTREE" ] && [ -n "$DB_ISOLATE" ]; then
    DB_NAME="schedulr_ralph_$(echo "$BRANCH" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9' '_' | sed 's/_*$//')"
    if docker exec -i schedulr-db \
        psql -U schedulr -d postgres -c "CREATE DATABASE \"$DB_NAME\"" >>"$LOG_FILE" 2>&1; then
        export DATABASE_URL="postgresql+psycopg://schedulr:schedulr@localhost:5433/$DB_NAME"
        (cd "$WORK_ROOT/app/backend" && uv run alembic upgrade head) >>"$LOG_FILE" 2>&1 \
            && echo "[db-isolate] isolated database '$DB_NAME' created and migrated." \
            || echo "[db-isolate] alembic upgrade failed on '$DB_NAME' (see log)."
    else
        echo "[db-isolate] could not create '$DB_NAME'; using shared DB (parallel runs collide)."
        DB_NAME=""
    fi
fi

cd "$WORK_ROOT"
echo "=== Ralph loop started at $(date) ===" | tee -a "$LOG_FILE"
echo "PROMPT: $PROMPT_FILE" | tee -a "$LOG_FILE"
echo "MAX_ITER: $MAX_ITER | TIMEOUT per iter: ${ITER_TIMEOUT}s" | tee -a "$LOG_FILE"

DONE=""
ITER=0
while [ "$ITER" -lt "$MAX_ITER" ]; do
    ITER=$((ITER + 1))
    echo "" | tee -a "$LOG_FILE"
    echo "--- Iteration $ITER / $MAX_ITER at $(date) ---" | tee -a "$LOG_FILE"

    if [ -f "$DONE_FILE" ]; then
        echo "DONE.txt found - spec complete after $((ITER - 1)) iterations." | tee -a "$LOG_FILE"
        DONE=1; break
    fi

    timeout "$ITER_TIMEOUT" \
        "$CLAUDE_BIN" -p \
            --output-format json \
            --dangerously-skip-permissions \
            --max-turns 40 \
        < "$PROMPT_FILE" \
        >> "$LOG_FILE" 2>&1 || {
            EXIT=$?
            if [ "$EXIT" -eq 124 ]; then
                echo "Iteration $ITER timed out after ${ITER_TIMEOUT}s" | tee -a "$LOG_FILE"
            else
                echo "Claude exited with code $EXIT" | tee -a "$LOG_FILE"
            fi
        }

    git add -A
    git diff --cached --quiet || git commit \
        -m "ralph: iteration $ITER - $(date +%Y-%m-%dT%H:%M:%S)" \
        --no-verify 2>&1 | tee -a "$LOG_FILE"

    if [ -f "$DONE_FILE" ]; then
        echo "DONE.txt found - spec complete after $ITER iterations." | tee -a "$LOG_FILE"
        DONE=1; break
    fi
    echo "Iteration $ITER complete - spec not yet done." | tee -a "$LOG_FILE"
done

if [ -z "$DONE" ]; then
    echo "MAX_ITER ($MAX_ITER) reached without DONE.txt. Review ralph.log and fix_plan.md." | tee -a "$LOG_FILE"
fi

if [ -n "$WORKTREE" ] && [ -n "$CLEANUP" ] && [ -n "$DONE" ]; then
    git -C "$REPO_ROOT" worktree remove "$WORK_ROOT" --force || true
    echo "cleanup: removed worktree $WORK_ROOT (branch '$BRANCH' kept)"
fi

if [ -n "$WORKTREE" ]; then
    echo ""
    echo "================================================================"
    echo "Ralph worktree run summary"
    echo "  Result:   $([ -n "$DONE" ] && echo 'DONE' || echo 'stopped (cap/timeout)')"
    echo "  Branch:   $BRANCH"
    echo "  Worktree: $WORK_ROOT"
    echo "  Database: ${DB_NAME:-shared (schedulr) - not isolated}"
    echo "  Review:   git -C \"$REPO_ROOT\" diff main..$BRANCH"
    echo "  Discard:  git -C \"$REPO_ROOT\" worktree remove \"$WORK_ROOT\" --force && git -C \"$REPO_ROOT\" branch -D $BRANCH"
    echo "================================================================"
fi

[ -n "$DONE" ] && exit 0 || exit 1
