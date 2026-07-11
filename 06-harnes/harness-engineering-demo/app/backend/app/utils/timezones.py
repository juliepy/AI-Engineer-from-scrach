"""Timezone-aware time rendering.

This is the *intended* way to render a stored UTC datetime in a viewer's timezone.
The AI Layer rule (stage-1) is: never format meeting datetimes with a naive
``strftime`` on the raw UTC value — always go through ``TimezoneAwareTime``.

The export path deliberately does NOT use this (that's the SCH-203 bug).
"""
from datetime import datetime
from zoneinfo import ZoneInfo

DISPLAY_FORMAT = "%Y-%m-%d %H:%M %Z"


class TimezoneAwareTime:
    """Render a UTC datetime in a target IANA timezone, correctly."""

    def __init__(self, value: datetime):
        self.value = value

    def in_zone(self, tz_name: str) -> datetime:
        tz = ZoneInfo(tz_name or "UTC")
        return self.value.astimezone(tz)

    def render(self, tz_name: str, fmt: str = DISPLAY_FORMAT) -> str:
        return self.in_zone(tz_name).strftime(fmt)
