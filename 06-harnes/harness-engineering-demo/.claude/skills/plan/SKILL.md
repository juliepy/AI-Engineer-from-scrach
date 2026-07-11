---
name: plan
description: Analyze a ticket or feature description, read the codebase, identify risks, and write a context-rich implementation plan to plans/<feature-slug>-plan.md. No code is written in this phase.
disable-model-invocation: true
---

# /plan — Analyze + Plan a Feature

**Usage:** `/plan <ticket-or-feature-description>`

Produces a context-rich implementation plan. **No code is written in this phase.**

---

## Process

### 1. Understand the ticket

Extract from `$ARGUMENTS`:
- Feature type (new capability / enhancement / bug fix / refactor)
- Affected resources and layers (model, schema, service, route, frontend)
- Acceptance criteria

### 2. Read the codebase

Load `CLAUDE.md` first for naming + pattern rules. Then read:

- Every existing file that will be **modified** — get real line numbers.
- The closest analogue to what you're building (e.g., building CSV export → read `export_service.py` and `routes_meetings.py:70-88`).
- Load relevant `.claude/context/` modules (see the on-demand table in `CLAUDE.md`).

Identify:
- Files to modify (with line refs)
- New files to create
- Migration needed? (any new table or column → yes)

### 3. Think through risks

- Edge cases (empty lists, null fields, concurrent requests)
- Security surface (user-supplied input → escape it; see export-pattern context for CSV)
- Timezone pitfalls (any datetime rendering → load timezones context)
- Auth path (new route → must use `auth_jwt.get_current_user`)
- Test coverage gap (what's not tested that could regress)

### 4. Write the plan to a file

Use the **Write tool** to create the file `plans/<feature-slug>-plan.md` — this is a required deliverable, not optional. Do **NOT** just print the plan in your response; `/implement` reads it from disk, so the file must exist. Use this structure:

```markdown
# Plan: <Feature Name>

## Ticket
<ticket ID and one-sentence description>

## Affected Files
### Read before implementing
- `<path>` (lines N-M) — <why>
### Modify
- `<path>` — <what changes>
### Create
- `<path>` — <purpose>

## Ordered Tasks

### Task 1 — <action> <target>
- What: <specific change>
- Pattern: `<path>:L<line>` — <what to mirror>
- Gotcha: <known trap if any>
- Validate: `<exact shell command>`

### Task 2 — ...

(continue for all tasks in dependency order)

## Validation Gate
Run these in order after all tasks are done:
\`\`\`
cd app/backend && uv run ruff check app
cd app/backend && uv run mypy app
cd app/backend && uv run pytest
cd app/frontend && npx tsc --noEmit
cd app/frontend && npm run test
\`\`\`

## Acceptance Criteria
- [ ] <measurable criterion 1>
- [ ] <measurable criterion 2>
- [ ] All validation gate commands pass
```

### 5. Confirm

After writing the plan file, output:
- Path: `plans/<feature-slug>-plan.md`
- Complexity: Low / Medium / High
- Key risks
- Confidence score (N/10 that `/implement` will succeed first-pass)

---

**Handoff:** Pass the plan path to `/implement plans/<feature-slug>-plan.md`.
