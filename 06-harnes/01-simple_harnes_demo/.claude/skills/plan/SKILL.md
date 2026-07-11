# /plan skill (minimal)

Goal: turn a user request into a short, testable plan.

## Output (required)

**You MUST create a new markdown file** under `plans/` named `<feature>-plan.md`.

Do not only describe the plan in chat. The file on disk is the deliverable.

After writing, tell the user the exact path, e.g. `plans/explain-strength-plan.md`.

## Template

```md
# <feature> plan

## Scope
- ...

## Tasks
- [ ] Task 1
- [ ] Task 2

## Validation
- python scripts/validate.py
```

## Rules

- Keep tasks small and ordered.
- Mention affected files.
- Include at least one test task.
