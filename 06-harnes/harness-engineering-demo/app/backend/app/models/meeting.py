from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    title: Mapped[str] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Stored as timezone-aware UTC. The BUG is in how these get *formatted* for
    # display/export (naive strftime ignoring the viewer tz) — not in storage.
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # The meeting's own tz label (e.g. "America/Chicago"); also under-used by the bug.
    meeting_timezone: Mapped[str] = mapped_column(String(64), default="UTC")

    status: Mapped[str] = mapped_column(String(32), default="scheduled")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    host: Mapped["User"] = relationship()  # type: ignore[name-defined]  # noqa: F821
    invitees: Mapped[list["MeetingInvitee"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )


class MeetingInvitee(Base):
    __tablename__ = "meeting_invitees"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), index=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), index=True)
    response: Mapped[str] = mapped_column(String(32), default="pending")

    meeting: Mapped["Meeting"] = relationship(back_populates="invitees")
    contact: Mapped["Contact"] = relationship()  # type: ignore[name-defined]  # noqa: F821
