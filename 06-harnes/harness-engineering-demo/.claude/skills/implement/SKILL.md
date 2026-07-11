---
name: implement
description: Read a plan file, execute every task in dependency order with per-task validation, then write an implementation report to reports/<feature-slug>-implementation-report.md.
disable-model-invocation: true
---

# /implement — Execute a Feature Plan

**Usage:** `/implement plans/<feature-slug>-plan.md`

Reads the plan at `$ARGUMENTS`, executes every task in order, runs each task's validation command, then writes an implementation report.

---

## Process

### 1. Read the full plan

Open the plan file given in `$ARGUMENTS`. Read it entirely before writing any code. Understand all tasks, their order, and the acceptance criteria.

Load any `.claude/context/` modules referenced in the plan's "Read before implementing" section.

### 2. Execute tasks in dependency order

For each task:

1. **Read** the target file(s) before editing — never overwrite blindly.
2. **Implement** the change following the stated pattern reference.
3. **Run** the task's `Validate:` command immediately. If it fails, fix before continuing.
4. Never skip a task's validation to move faster — a skipped check is a hidden regression.

### 3. Apply the full validation gate

After all tasks complete, run the full gate from the plan's "Validation Gate" section:

```
cd app/backend && uv run ruff check app
cd app/backend && uv run mypy app
cd app/backend && uv run pytest
cd app/frontend && npx tsc --noEmit
cd app/frontend && npm run test
```

If any command fails: fix, re-run that command, then re-run the full gate. Do not declare done until every command is green.

### 4. Write the implementation report

Output to `reports/<feature-slug>-implementation-report.md`:

```markdown
# Implementation Report: <Feature Name>

## Plan
`plans/<feature-slug>-plan.md`

## Tasks Completed
| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | <description> | DONE | |
| 2 | <description> | DONE | |

## Files Changed
- **Created:** `<path>`
- **Modified:** `<path>` (lines changed: N–M)

## Validation Gate Results
| Command | Result |
|---------|--------|
| `uv run ruff check app` | PASS |
| `uv run mypy app` | PASS |
| `uv run pytest` | PASS (N tests) |
| `npx tsc --noEmit` | PASS |
| `npm run test` (vitest) | PASS |

## Acceptance Criteria
- [x] <criterion>
- [x] <criterion>

## Issues / Deviations
<any deviation from the plan and why>

## Ready for Review
All tasks done. All validation gate commands green. Ready for `/validate` and commit.
```

---

**Handoff:** Run `/validate` to confirm the full gate before committing.
