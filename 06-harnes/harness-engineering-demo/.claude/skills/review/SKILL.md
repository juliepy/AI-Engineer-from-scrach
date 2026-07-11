---
name: review
description: Delegate the latest implementation diff to the code-reviewer sub-agent for a PASS/CONCERNS verdict against CLAUDE.md rules, then write the verdict to reports/<feature>-review.md.
disable-model-invocation: true
---

# /review — Sub-Agent Code Review

**Usage:** `/review` (run after `/implement` and before committing)

Delegates the implementation diff to the `code-reviewer` sub-agent, which checks it against `CLAUDE.md` rules (naming, patterns, CSV escaping, JWT auth, route ordering) using the `codebase-search` MCP tools for structural verification. Writes the verdict to `reports/<feature>-review.md`.

---

## Process

### 1. Identify the implementation report

Find the most recent file in `reports/` matching `*-implementation-report.md`. That report names the feature slug and the files changed.

### 2. Gather the diff

Run:
```bash
git diff HEAD
```

If the changes are already committed (e.g., after `/validate`), run:
```bash
git show HEAD
```

### 3. Delegate to the code-reviewer sub-agent

Invoke the `code-reviewer` sub-agent with:
- The full diff text
- The feature slug (from the implementation report)
- A reminder to use `find_references` / `where_is` to verify call sites

### 4. Write the review report

Write the sub-agent's verdict to `reports/<feature-slug>-review.md` using the Write tool. Do not modify the verdict.

### 5. Report back

Output:
- Path: `reports/<feature-slug>-review.md`
- Verdict: PASS or CONCERNS
- If CONCERNS: list the blocking items that must be resolved before committing

---

**Handoff:** If PASS, commit. If CONCERNS, fix the flagged issues and re-run `/validate` then `/review`.
