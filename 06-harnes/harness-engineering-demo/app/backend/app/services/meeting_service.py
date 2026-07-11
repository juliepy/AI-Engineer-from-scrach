"""Meeting queries + serialization.

Timezone handling: uses ``TimezoneAwareTime`` to render datetimes in the
viewer's timezone.  The naive-strftime bug (SCH-203) has been removed —
timezone rendering is now correct.  The workshop's system-evolution subject
is the future CSV export (SCH-142) and its formula-injection escaping.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Meeting
from app.utils.timezones import TimezoneAwareTime


def _format_when(dt: datetime, tz_name: str = "UTC") -> str:
    return TimezoneAwareTime(dt).render(tz_name)


def list_meetings(
    db: Session,
    team_id: int,
    host_id: int | None = None,
    start_after: datetime | None = None,
    start_before: datetime | None = None,
    contact_id: int | None = None,
    status: str | None = None,
    search: str | None = None,
    viewer_tz: str = "UTC",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    stmt = (
        select(Meeting)
        .where(Meeting.team_id == team_id)
        .order_by(Meeting.start_time.desc())
    )
    if host_id is not None:
        stmt = stmt.where(Meeting.host_id == host_id)
    if start_after is not None:
        stmt = stmt.where(Meeting.start_time >= start_after)
    if start_before is not None:
        stmt = stmt.where(Meeting.start_time <= start_before)
    if status is not None:
        stmt = stmt.where(Meeting.status == status)
    if search is not None:
        stmt = stmt.where(Meeting.title.ilike(f"%{search}%"))

    if contact_id is not None:
        from app.models import MeetingInvitee as MI
        stmt = stmt.join(MI, MI.meeting_id == Meeting.id).where(MI.contact_id == contact_id)

    stmt = stmt.offset(offset).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return [serialize_meeting(m, viewer_tz=viewer_tz) for m in rows]


def serialize_meeting(m: Meeting, viewer_tz: str = "UTC", include_invitees: bool = False) -> dict:
    out: dict = {
        "id": m.id,
        "title": m.title,
        "host": m.host.full_name if m.host else None,
        "host_id": m.host_id,
        "start": _format_when(m.start_time, viewer_tz),
        "end": _format_when(m.end_time, viewer_tz),
        "timezone": m.meeting_timezone,
        "status": m.status,
        "notes": m.notes,
        "inviteeCount": len(m.invitees),
    }
    if include_invitees:
        out["invitees"] = [
            {
                "id": inv.id,
                "contact_id": inv.contact_id,
                "contact_name": inv.contact.name if inv.contact else "",
                "contact_email": inv.contact.email if inv.contact else "",
                "response": inv.response,
            }
            for inv in m.invitees
        ]
    else:
        out["invitees"] = []
    return out


def get_meeting(db: Session, meeting_id: int, team_id: int, viewer_tz: str = "UTC") -> dict | None:
    m = db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.team_id == team_id)
    ).scalar_one_or_none()
    if m is None:
        return None
    return serialize_meeting(m, viewer_tz=viewer_tz, include_invitees=True)
