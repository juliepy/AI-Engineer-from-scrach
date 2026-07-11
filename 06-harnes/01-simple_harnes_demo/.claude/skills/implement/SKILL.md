# /implement skill (minimal)

Goal: execute tasks from a plan file safely.

## Steps

1. Read the plan from `plans/*.md`.
2. Complete tasks one by one.
3. After each task, run relevant tests.
4. At the end, run full validation.
5. Write `reports/<feature>-implementation-report.md`.

## Report template

```md
# <feature> implementation report

## Completed tasks
- ...

## Files changed
- ...

## Validation result
- python scripts/validate.py: PASS/FAIL
```
