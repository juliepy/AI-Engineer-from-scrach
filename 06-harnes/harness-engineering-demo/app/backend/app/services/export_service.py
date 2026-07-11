"""Export pipeline.

``ExportService`` is the base; ``PDFExport`` is the one concrete exporter that
exists today. SCH-142 ("Add CSV export to meetings page") asks for a CSVExport
that mirrors this pattern — that's what the workshop builds live.

NOTE: The timezone bug (SCH-203) has been fixed — ``PDFExport`` now uses
``TimezoneAwareTime`` to render datetimes in the viewer's timezone.
The workshop's system-evolution subject is the CSV export (SCH-142) and its
formula-injection escaping — a naive CSV implementation that writes user-
controlled data directly into cells can be exploited via ``=HYPERLINK(...)``
or similar formulas. The ``/system-gap`` skill should catch this.
"""
from datetime import datetime
from typing import Protocol

from app.models import Meeting
from app.utils.timezones import TimezoneAwareTime


DISPLAY_FORMAT = "%Y-%m-%d %H:%M %Z"


class ExportService(Protocol):
    content_type: str
    file_extension: str

    def render(self, meetings: list[Meeting], viewer_tz: str = "UTC") -> bytes: ...


def _format_when(dt: datetime, tz_name: str = "UTC") -> str:
    return TimezoneAwareTime(dt).render(tz_name)


class PDFExport:
    content_type = "application/pdf"
    file_extension = "pdf"

    def render(self, meetings: list[Meeting], viewer_tz: str = "UTC") -> bytes:
        # Minimal stand-in for a real PDF renderer (the demo doesn't open PDFs).
        lines = ["Meetings Export (PDF)", "=" * 24]
        for m in meetings:
            lines.append(f"{m.title} | {_format_when(m.start_time, viewer_tz)} | {m.status}")
        return ("\n".join(lines)).encode("utf-8")
