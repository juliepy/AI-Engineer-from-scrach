from datetime import datetime

from pydantic import BaseModel


class MeetingCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    meeting_timezone: str = "UTC"
    notes: str | None = None
    invitee_contact_ids: list[int] = []


class MeetingUpdate(BaseModel):
    title: str | None = None
    notes: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    meeting_timezone: str | None = None
    status: str | None = None


class RSVPUpdate(BaseModel):
    response: str  # "accepted" | "declined" | "pending"


class InviteeOut(BaseModel):
    id: int
    contact_id: int
    contact_name: str
    contact_email: str
    response: str


class MeetingOut(BaseModel):
    id: int
    title: str
    host: str | None
    host_id: int
    start: str
    end: str
    timezone: str
    status: str
    notes: str | None
    inviteeCount: int
    invitees: list[InviteeOut] = []
