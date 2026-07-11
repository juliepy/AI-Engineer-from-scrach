# Timezones — Schedulr

## The Golden Rule

**All meeting datetimes are stored as UTC** (`DateTime(timezone=True)`).  
**All rendering uses `TimezoneAwareTime`** — never call `.strftime()` on a raw datetime.

## `TimezoneAwareTime` (`app/backend/app/utils/timezones.py`)

```python
class TimezoneAwareTime:
    def __init__(self, value: datetime): ...
    def in_zone(self, tz_name: str) -> datetime: ...
    def render(self, tz_name: str, fmt: str = DISPLAY_FORMAT) -> str: ...
```

`DISPLAY_FORMAT = "%Y-%m-%d %H:%M %Z"` — yields e.g. `"2026-07-20 16:00 CEST"`.

### Correct usage

```python
from app.utils.timezones import TimezoneAwareTime

# In a serializer or export renderer:
displayed = TimezoneAwareTime(meeting.start_time).render(viewer_tz)
```

### Wrong (the bug pattern — SCH-203)

```python
# DO NOT DO THIS — ignores viewer timezone, always shows UTC
displayed = meeting.start_time.strftime("%Y-%m-%d %H:%M")
```

## Where `viewer_tz` Comes From

- `current.timezone` — the authenticated user's IANA timezone string (e.g. `"America/Chicago"`), stored on `User.timezone` (`app/backend/app/models/user.py:17`).
- Always passed into service-layer functions as `viewer_tz: str` parameter — see `list_meetings()` and `serialize_meeting()` in `app/backend/app/services/meeting_service.py`.

## `meeting_timezone`

`Meeting.meeting_timezone` (`app/backend/app/models/meeting.py:25`) stores the timezone in which the meeting was **created**. This is distinct from the viewer's timezone. It is stored on the model and surfaced in the `MeetingOut` schema as `timezone`. Do not confuse the two.

## Validating Timezone Correctness

Tests that cover non-UTC rendering are in `app/backend/app/tests/test_timezone.py` and `test_export.py:TestFormatWhen`. When adding any new datetime-rendering path, add a test that asserts a UTC time and a Berlin/Chicago time produce **different** strings.

## IANA Timezone Validation

`app/backend/app/utils/misc.py` (or a dedicated validator) may contain `validate_timezone()`. When accepting a timezone name from user input, always validate against `zoneinfo.available_timezones()` and raise `HTTPException(400, ...)` on an unknown value.
