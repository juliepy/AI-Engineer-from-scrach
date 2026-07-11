from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)

    name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # crm-ish fields
    stage: Mapped[str] = mapped_column(String(40), default="lead")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    meeting_links: Mapped[list["ContactMeetingLink"]] = relationship(  # type: ignore[name-defined]  # noqa: F821
        back_populates="contact", cascade="all, delete-orphan"
    )


class ContactMeetingLink(Base):
    """Many-to-many link between contacts and meetings (separate from MeetingInvitee)."""
    __tablename__ = "contact_meeting_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"), index=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"), index=True)

    contact: Mapped["Contact"] = relationship(back_populates="meeting_links")  # type: ignore[name-defined]  # noqa: F821
    meeting: Mapped["Meeting"] = relationship()  # type: ignore[name-defined]  # noqa: F821
