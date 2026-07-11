# Export Pattern — Schedulr

## Protocol

**File:** `app/backend/app/services/export_service.py`

`ExportService` is a `Protocol` (structural subtyping):

```python
class ExportService(Protocol):
    content_type: str
    file_extension: str
    def render(self, meetings: list[Meeting], viewer_tz: str = "UTC") -> bytes: ...
```

To add a new format, create a class that satisfies the protocol — no inheritance needed.

## Existing Exporter: PDFExport

`PDFExport` (`export_service.py:35`) renders meeting times through `_format_when()` which calls `TimezoneAwareTime.render()`. This is the **correct** pattern — times always arrive in viewer timezone.

## Adding CSV Export (SCH-142 — workshop target)

**Route:** `app/backend/app/api/routes_meetings.py:70` — `GET /api/meetings/export?format=pdf`. Add `format=csv` branch here.

### Formula Injection (Critical Security Rule)

CSV cells that start with `=`, `+`, `-`, or `@` are interpreted as formulas by Excel/Google Sheets. Any user-supplied string (title, notes, contact name, email) must be sanitized before writing:

```python
FORMULA_PREFIXES = ("=", "+", "-", "@")

def csv_safe(value: str) -> str:
    """Escape formula-injection in CSV cells."""
    if value and value[0] in FORMULA_PREFIXES:
        return "'" + value  # prefix with single-quote: Excel treats as literal text
    return value
```

Apply `csv_safe()` to every cell derived from user input. Fields at risk:
- `meeting.title` (user-controlled)
- `meeting.notes` (user-controlled)
- contact name/email from `MeetingInvitee.contact`

### Implementation Checklist for CSVExport

1. Add `CSVExport` class to `export_service.py` — satisfies `ExportService` protocol.
2. Use Python stdlib `csv.writer` (already available; no new dependency).
3. Header row: `["ID", "Title", "Start", "End", "Timezone", "Status", "Invitees"]`.
4. Render times through `_format_when(dt, viewer_tz)` (same as PDFExport).
5. Apply `csv_safe()` to `title`, `notes`, and all contact fields.
6. Return `bytes` — encode as `"utf-8-sig"` (BOM) for Excel compatibility.
7. Wire into the export route: `elif format == "csv": exporter = CSVExport()`.
8. Return with `Content-Disposition: attachment; filename=meetings.csv`.

### Test Pattern

See `app/backend/app/tests/test_export.py` for how PDFExport is tested. Mirror it: test that `render([])` returns bytes, verify a non-default `viewer_tz` produces a different time string, and add a formula-injection test:

```python
def test_csv_formula_injection_escaped():
    m = make_meeting(title="=HYPERLINK(\"http://evil.com\",\"Click\")")
    result = CSVExport().render([m], viewer_tz="UTC").decode("utf-8-sig")
    assert '=HYPERLINK' not in result.split("\n")[1]  # title cell must not start with =
```
