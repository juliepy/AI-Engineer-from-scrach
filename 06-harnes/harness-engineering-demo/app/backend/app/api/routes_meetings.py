from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Meeting, MeetingInvitee, User
from app.schemas.meeting import MeetingCreate, MeetingUpdate, RSVPUpdate
from app.services.auth_jwt import get_current_user
from app.services.export_service import PDFExport
from app.services.meeting_service import list_meetings, serialize_meeting, get_meeting

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("")
def get_meetings(
    host_id: int | None = Query(default=None),
    start_after: datetime | None = Query(default=None),
    start_before: datetime | None = Query(default=None),
    contact_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_meetings(
        db,
        team_id=current.team_id,
        host_id=host_id,
        start_after=start_after,
        start_before=start_before,
        contact_id=contact_id,
        status=status,
        search=search,
        viewer_tz=current.timezone,
        limit=limit,
        offset=offset,
    )


@router.post("", status_code=201)
def create_meeting(
    payload: MeetingCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = Meeting(
        team_id=current.team_id,
        host_id=current.id,
        title=payload.title,
        notes=payload.notes,
        start_time=payload.start_time,
        end_time=payload.end_time,
        meeting_timezone=payload.meeting_timezone,
    )
    db.add(m)
    db.flush()
    for cid in payload.invitee_contact_ids:
        db.add(MeetingInvitee(meeting_id=m.id, contact_id=cid))
    db.commit()
    db.refresh(m)
    return serialize_meeting(m, viewer_tz=current.timezone, include_invitees=True)


@router.get("/export")
def export_meetings(
    format: str = Query(default="pdf"),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only PDF export exists today. SCH-142 adds CSV (the workshop builds it live).
    if format != "pdf":
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {format}")
    meetings = (
        db.execute(select(Meeting).where(Meeting.team_id == current.team_id)).scalars().all()
    )
    exporter = PDFExport()
    body = exporter.render(list(meetings), viewer_tz=current.timezone)
    return Response(
        content=body,
        media_type=exporter.content_type,
        headers={"Content-Disposition": f"attachment; filename=meetings.{exporter.file_extension}"},
    )


@router.get("/{meeting_id}")
def get_meeting_detail(
    meeting_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = get_meeting(db, meeting_id, current.team_id, viewer_tz=current.timezone)
    if result is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return result


@router.patch("/{meeting_id}")
def update_meeting(
    meeting_id: int,
    payload: MeetingUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.team_id == current.team_id)
    ).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    # Only host or admin can update
    if m.host_id != current.id and current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if payload.title is not None:
        m.title = payload.title
    if payload.notes is not None:
        m.notes = payload.notes
    if payload.start_time is not None:
        m.start_time = payload.start_time
    if payload.end_time is not None:
        m.end_time = payload.end_time
    if payload.meeting_timezone is not None:
        m.meeting_timezone = payload.meeting_timezone
    if payload.status is not None:
        m.status = payload.status
    db.commit()
    db.refresh(m)
    return serialize_meeting(m, viewer_tz=current.timezone, include_invitees=True)


@router.delete("/{meeting_id}", status_code=204)
def cancel_meeting(
    meeting_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    m = db.execute(
        select(Meeting).where(Meeting.id == meeting_id, Meeting.team_id == current.team_id)
    ).scalar_one_or_none()
    if m is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    if m.host_id != current.id and current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    m.status = "cancelled"
    db.commit()


@router.patch("/{meeting_id}/invitees/{invitee_id}/rsvp")
def update_rsvp(
    meeting_id: int,
    invitee_id: int,
    payload: RSVPUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    inv = db.execute(
        select(MeetingInvitee).where(
            MeetingInvitee.id == invitee_id,
            MeetingInvitee.meeting_id == meeting_id,
        )
    ).scalar_one_or_none()
    if inv is None:
        raise HTTPException(status_code=404, detail="Invitee not found")
    # Ensure meeting is in this team
    m = db.get(Meeting, meeting_id)
    if m is None or m.team_id != current.team_id:
        raise HTTPException(status_code=404, detail="Meeting not found")
    valid = {"accepted", "declined", "pending"}
    if payload.response not in valid:
        raise HTTPException(status_code=400, detail=f"Response must be one of {valid}")
    inv.response = payload.response
    db.commit()
    return {"id": inv.id, "response": inv.response}
