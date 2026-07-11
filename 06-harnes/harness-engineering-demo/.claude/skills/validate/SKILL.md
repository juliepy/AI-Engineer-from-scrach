---
name: validate
description: Run the full quality gate (ruff + mypy + pytest + tsc + vitest) and report PASS/FAIL for each command. Run before any commit or PR.
disable-model-invocation: true
---

# /validate — Full Validation Gate

Run the complete quality gate and report PASS/FAIL for each command.

This is the same gate the `Stop` hook enforces automatically. Run it explicitly before any commit or PR.

---

## Gate Commands

```bash
# Backend
cd app/backend && uv run ruff check app
cd app/backend && uv run mypy app
cd app/backend && uv run pytest

# Frontend
# NOTE: this brownfield app ships NO ESLint config, so `next lint` prompts
# interactively (it would hang an automated gate). Static checking is done with
# the TypeScript compiler; vitest covers unit tests. Wiring up ESLint is a
# real follow-up the harness/workshop would flag.
cd app/frontend && npx tsc --noEmit
cd app/frontend && npm run test
```

---

## Report Format

After running all commands, output:

```
Validation Gate Results
=======================

Backend
  ruff check app     : PASS / FAIL
  mypy app           : PASS / FAIL
  pytest             : PASS (N tests) / FAIL (N failed, N passed)

Frontend
  tsc --noEmit       : PASS / FAIL
  vitest (npm test)  : PASS / FAIL

Overall: PASS / FAIL
```

If **FAIL**: list each failing command with the first error or failure message. Fix the issue and re-run `/validate` before proceeding.

If **PASS**: the working tree is clean and ready to commit.

---

## Notes

- The `Stop` hook (`stop_validate.py`) runs this gate automatically when Claude finishes a turn. If it blocks, you'll see the reason in the hook output — fix and let Claude continue.
- If you're only touching backend code, the frontend commands will still run but failures there do not indicate a regression in your change — investigate and fix anyway before merging.
- Mypy config is in `app/backend/pyproject.toml`. The `jose` module has `ignore_missing_imports = true` (see `pyproject.toml:40`).
