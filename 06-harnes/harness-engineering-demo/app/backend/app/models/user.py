from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(160))
    # smell: IANA tz string per user, but it gets ignored in the export path (the bug)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    role: Mapped[str] = mapped_column(String(32), default="member")

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    team: Mapped["Team"] = relationship(back_populates="users")  # type: ignore[name-defined]  # noqa: F821

    # smell: camelCase column name in an otherwise snake_case schema
    createdAt: Mapped[datetime] = mapped_column(
        "createdAt", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
