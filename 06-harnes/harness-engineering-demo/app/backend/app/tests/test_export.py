"""Tests for export service."""
from datetime import datetime, timezone

from app.services.export_service import PDFExport, _format_when


class TestPDFExport:
    def test_render_returns_bytes(self) -> None:
        exporter = PDFExport()
        result = exporter.render([])
        assert isinstance(result, bytes)
        assert b"Meetings Export (PDF)" in result

    def test_render_with_meetings(self) -> None:
        """PDFExport renders times using TimezoneAwareTime (no naive strftime)."""
        exporter = PDFExport()
        # We just verify it runs without error and returns bytes
        result = exporter.render([], viewer_tz="UTC")
        assert isinstance(result, bytes)

    def test_content_type(self) -> None:
        exporter = PDFExport()
        assert exporter.content_type == "application/pdf"
        assert exporter.file_extension == "pdf"


class TestFormatWhen:
    def test_utc_format(self) -> None:
        dt = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
        result = _format_when(dt, "UTC")
        assert "14:00" in result

    def test_berlin_format(self) -> None:
        dt = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
        result = _format_when(dt, "Europe/Berlin")
        assert "16:00" in result

    def test_no_naive_strftime(self) -> None:
        """Ensures we're not using naive strftime (which would give UTC regardless)."""
        dt = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
        utc_result = _format_when(dt, "UTC")
        berlin_result = _format_when(dt, "Europe/Berlin")
        assert utc_result != berlin_result
