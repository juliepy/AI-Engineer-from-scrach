# Ralph Spec: Add CSV Export (SCH-142)

## Goal

Add a `CSVExport` class to the Schedulr backend and wire it into the existing export route so that `GET /api/meetings/export?format=csv` returns a UTF-8 CSV file with formula-injection escaping.

## Spec Items (all must pass for DONE)

1. `app/backend/app/services/export_service.py` contains a `CSVExport` class that satisfies the `ExportService` protocol (has `content_type`, `file_extension`, and `render(meetings, viewer_tz) -> bytes`).
2. `CSVExport.render()` uses `csv.writer` from the Python stdlib (no new dependency).
3. All user-supplied string fields (title, notes, contact names, emails) are passed through a `csv_safe()` helper that prefixes `=`, `+`, `-`, `@` leading characters with a single-quote.
4. Times are rendered through `_format_when(dt, viewer_tz)` - no raw `.strftime()`.
5. `GET /api/meetings/export?format=csv` returns HTTP 200 with `Content-Type: text/csv` and a `Content-Disposition: attachment; filename=meetings.csv` header.
6. `app/backend/app/tests/test_export.py` includes at least one test for `CSVExport.render()` returning bytes and one test proving formula-injection is escaped.
7. `cd app/backend && uv run ruff check app` passes (exit 0).
8. `cd app/backend && uv run pytest` passes (exit 0, no failures).

## Work Pattern

- Do ONE logical change per loop iteration.
- After each change, run the appropriate validation command and record the result in `ralph/fix_plan.md`.
- When ALL 8 spec items are satisfied AND all validation commands pass, run `touch ralph/DONE.txt`.
- Do NOT touch `ralph/DONE.txt` until all 8 items are confirmed passing.

## Fix Plan File

Maintain `ralph/fix_plan.md` - append each iteration's result:

```
## Iteration N
- Did: <what you changed>
- Validation: `<command>` -> PASS/FAIL
- Next: <what's left>
```
