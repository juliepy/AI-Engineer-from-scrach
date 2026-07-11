# Produced changes - CSV export (SCH-142)

The code this Ralph run committed across its 4 iterations. Each spec item maps to something below. This is a reference snapshot; the live repo stays demo-fresh so the feature can be built on camera.

---

## 1. `app/backend/app/services/export_service.py` (modified)

Added the `csv_safe()` helper and the `CSVExport` class alongside the existing `PDFExport`. Satisfies spec items 1-4.

```python
import csv
import io
from datetime import datetime
from typing import Protocol

from app.models import Meeting
from app.utils.timezones import TimezoneAwareTime


# ... ExportService protocol, _format_when, PDFExport unchanged ...


_FORMULA_PREFIXES = ("=", "+", "-", "@")


def csv_safe(value: str) -> str:
    """Neutralise CSV formula injection.

    Spreadsheet apps execute a cell that starts with =, +, -, or @. Prefixing a
    single quote forces the cell to be treated as text. See SCH-142.
    """
    if value and value[0] in _FORMULA_PREFIXES:
        return "'" + value
    return value


class CSVExport:
    content_type = "text/csv"
    file_extension = "csv"

    def render(self, meetings: list[Meeting], viewer_tz: str = "UTC") -> bytes:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Title", "When", "Status", "Notes"])
        for m in meetings:
            writer.writerow([
                csv_safe(m.title),
                _format_when(m.start_time, viewer_tz),   # spec item 4: no raw strftime
                csv_safe(m.status),
                csv_safe(m.notes or ""),
            ])
        return buf.getvalue().encode("utf-8")
```

---

## 2. `app/backend/app/api/routes_meetings.py` (modified)

Wired `CSVExport` into the existing export route through a format map. Satisfies spec item 5.

```python
from app.services.export_service import CSVExport, PDFExport

_EXPORTERS = {"pdf": PDFExport, "csv": CSVExport}


@router.get("/export")
def export_meetings(
    format: str = Query(default="pdf"),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    exporter_cls = _EXPORTERS.get(format)
    if exporter_cls is None:
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
    meetings = (
        db.execute(select(Meeting).where(Meeting.team_id == current.team_id)).scalars().all()
    )
    exporter = exporter_cls()
    body = exporter.render(list(meetings), viewer_tz=current.timezone)
    return Response(
        content=body,
        media_type=exporter.content_type,
        headers={"Content-Disposition": f"attachment; filename=meetings.{exporter.file_extension}"},
    )
```

`format=csv` now returns `200` with `Content-Type: text/csv` and `Content-Disposition: attachment; filename=meetings.csv`.

---

## 3. `app/backend/app/tests/test_export.py` (modified)

Added CSV coverage. Satisfies spec item 6.

```python
from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.export_service import CSVExport, csv_safe


class TestCSVExport:
    def test_render_returns_bytes(self) -> None:
        result = CSVExport().render([])
        assert isinstance(result, bytes)
        assert b"Title,When,Status,Notes" in result

    def test_content_type(self) -> None:
        exporter = CSVExport()
        assert exporter.content_type == "text/csv"
        assert exporter.file_extension == "csv"

    def test_render_escapes_formula_injection(self) -> None:
        evil = SimpleNamespace(
            title="=HYPERLINK('http://evil', 'click')",
            status="confirmed",
            notes="",
            start_time=datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc),
        )
        out = CSVExport().render([evil], viewer_tz="UTC").decode("utf-8")
        assert "'=HYPERLINK" in out          # leading quote neutralises the formula


class TestCSVSafe:
    def test_escapes_formula_prefixes(self) -> None:
        assert csv_safe("=1+1") == "'=1+1"
        assert csv_safe("+ping") == "'+ping"
        assert csv_safe("-2") == "'-2"
        assert csv_safe("@cmd") == "'@cmd"

    def test_leaves_safe_values_untouched(self) -> None:
        assert csv_safe("Quarterly sync") == "Quarterly sync"
```

---

## Validation at the end of the run (spec items 7-8)

```
cd app/backend && uv run ruff check app     ->  All checks passed!
cd app/backend && uv run pytest             ->  87 passed
```

## Commits the loop produced

```
ralph: iteration 4 - 2026-05-26T09:23:10   add ralph/DONE.txt (all 8 spec items pass)
ralph: iteration 3 - 2026-05-26T09:22:03   tests: CSVExport + csv_safe (injection escaped)
ralph: iteration 2 - 2026-05-26T09:19:11   wire format=csv into the export route
ralph: iteration 1 - 2026-05-26T09:16:48   add csv_safe() + CSVExport to export_service.py
```
