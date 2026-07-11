# Fix Plan - CSV Export (SCH-142)

Running log maintained by Ralph across iterations (per the PROMPT.md work pattern). One logical change per iteration, each with its validation result.

## Iteration 1
- Did: Added `csv_safe()` helper and the `CSVExport` class to `app/backend/app/services/export_service.py`. Uses stdlib `csv.writer`, renders times via `_format_when`, and routes user string fields through `csv_safe()`.
- Validation: `cd app/backend && uv run ruff check app` -> PASS
- Next: wire `format=csv` into the export route.

## Iteration 2
- Did: Wired `CSVExport` into `GET /api/meetings/export` in `app/backend/app/api/routes_meetings.py` via a `{"pdf": PDFExport, "csv": CSVExport}` format map. CSV responses return `Content-Type: text/csv` and `Content-Disposition: attachment; filename=meetings.csv`.
- Validation: `cd app/backend && uv run ruff check app` -> PASS
- Next: add tests for `CSVExport` and the injection escaping.

## Iteration 3
- Did: Added `TestCSVExport` and `TestCSVSafe` to `app/backend/app/tests/test_export.py` - render returns bytes, correct content-type/extension, `csv_safe()` escapes `= + - @`, and a render-level test proving a `=HYPERLINK(...)` title is neutralised with a leading single-quote.
- Validation: `cd app/backend && uv run pytest` -> PASS (87 passed)
- Next: confirm all 8 spec items, run the full checks, signal DONE.

## Iteration 4
- Did: Re-read all 8 spec items against the diff. Ran ruff + pytest clean. Created `ralph/DONE.txt`.
- Validation: `cd app/backend && uv run ruff check app` -> PASS ; `cd app/backend && uv run pytest` -> PASS (87 passed)
- Next: none. Spec complete.

---

## Spec items (final state)

- [x] 1. `CSVExport` satisfies the `ExportService` protocol (`content_type`, `file_extension`, `render`).
- [x] 2. `render()` uses stdlib `csv.writer` (no new dependency).
- [x] 3. User string fields routed through `csv_safe()` (prefixes `=`, `+`, `-`, `@` with a single quote).
- [x] 4. Times rendered via `_format_when(dt, viewer_tz)` (no raw `.strftime()`).
- [x] 5. `GET /api/meetings/export?format=csv` -> 200, `Content-Type: text/csv`, `Content-Disposition: attachment; filename=meetings.csv`.
- [x] 6. `test_export.py` covers `CSVExport.render()` returning bytes and proves formula-injection is escaped.
- [x] 7. `cd app/backend && uv run ruff check app` passes (exit 0).
- [x] 8. `cd app/backend && uv run pytest` passes (exit 0).

**Result: DONE after 4 iterations.**
