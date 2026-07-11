"""Tests verifying correct timezone rendering.

These tests confirm that the SCH-203 bug has been fixed — datetimes are
now rendered in the viewer's timezone, not as raw UTC.
"""
from datetime import datetime, timezone

from app.models import Meeting
from app.utils.timezones import TimezoneAwareTime
from app.services.meeting_service import serialize_meeting


class TestTimezoneAwareTime:
    def test_utc_rendering(self) -> None:
        dt = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        t = TimezoneAwareTime(dt)
        rendered = t.render("UTC")
        assert "14:00" in rendered
        assert "UTC" in rendered

    def test_berlin_rendering(self) -> None:
        """14:00 UTC = 16:00 CEST (UTC+2 in July)."""
        dt = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        t = TimezoneAwareTime(dt)
        rendered = t.render("Europe/Berlin")
        assert "16:00" in rendered

    def test_chicago_rendering(self) -> None:
        """14:00 UTC = 09:00 CDT (UTC-5 in July)."""
        dt = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        t = TimezoneAwareTime(dt)
        rendered = t.render("America/Chicago")
        assert "09:00" in rendered

    def test_singapore_rendering(self) -> None:
        """14:00 UTC = 22:00 SGT (UTC+8 always)."""
        dt = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        t = TimezoneAwareTime(dt)
        rendered = t.render("Asia/Singapore")
        assert "22:00" in rendered

    def test_in_zone_returns_datetime(self) -> None:
        dt = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        t = TimezoneAwareTime(dt)
        berlin_dt = t.in_zone("Europe/Berlin")
        assert berlin_dt.hour == 16

    def test_fallback_to_utc_on_none(self) -> None:
        dt = datetime(2026, 7, 20, 14, 0, 0, tzinfo=timezone.utc)
        t = TimezoneAwareTime(dt)
        rendered = t.render(None)  # type: ignore[arg-type]
        assert "14:00" in rendered


class TestMeetingSerializerTimezone:
    """Test that serialize_meeting renders in the viewer tz, not raw UTC."""

    def test_serialize_in_berlin_tz(
        self, meeting: Meeting, db: object
    ) -> None:
        m = meeting
        result = serialize_meeting(m, viewer_tz="Europe/Berlin")
        # The fixture starts at 14:00 UTC → 16:00 Berlin
        assert "16:00" in result["start"]

    def test_serialize_in_utc_different_from_berlin(
        self, meeting: Meeting, db: object
    ) -> None:
        m = meeting
        utc_result = serialize_meeting(m, viewer_tz="UTC")
        berlin_result = serialize_meeting(m, viewer_tz="Europe/Berlin")
        # The times should differ
        assert utc_result["start"] != berlin_result["start"]
