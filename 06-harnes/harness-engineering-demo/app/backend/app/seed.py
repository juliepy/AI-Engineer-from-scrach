"""Seed Schedulr with realistic demo data.

Includes users across timezones (incl. Europe) so the SCH-203 timezone bug is
visible in the meetings list / export during the demo.

Run:  uv run python -m app.seed
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal, engine, Base
from app.models import Team, User, Meeting, MeetingInvitee, Contact, AvailabilitySlot
from app.services.security import hash_password


def run() -> None:
    Base.metadata.create_all(engine)  # safety net if migrations not yet applied
    db = SessionLocal()
    try:
        if db.execute(select(Team)).first():
            print("Seed data already present — skipping.")
            return

        team = Team(name="Acme Sales", slug="acme-sales")
        db.add(team)
        db.flush()

        users = [
            User(email="dana@acme.test", full_name="Dana Ortiz", timezone="America/Chicago",
                 role="admin", team_id=team.id, hashed_password=hash_password("password123")),
            User(email="lukas@acme.test", full_name="Lukas Berg", timezone="Europe/Berlin",
                 role="member", team_id=team.id, hashed_password=hash_password("password123")),
            User(email="mei@acme.test", full_name="Mei Tan", timezone="Asia/Singapore",
                 role="member", team_id=team.id, hashed_password=hash_password("password123")),
        ]
        db.add_all(users)
        db.flush()

        contacts = [
            Contact(team_id=team.id, name="Priya Shah", email="priya@globex.test",
                    company="Globex", stage="opportunity"),
            Contact(team_id=team.id, name="Tom Reeves", email="tom@initech.test",
                    company="Initech", stage="lead"),
            Contact(team_id=team.id, name="Sofia Marin", email="sofia@umbrella.test",
                    company="Umbrella", stage="customer"),
        ]
        db.add_all(contacts)
        db.flush()

        base = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)  # 14:00 UTC
        for i in range(12):
            host = users[i % len(users)]
            start = base + timedelta(days=i, hours=(i % 3))
            m = Meeting(
                team_id=team.id,
                host_id=host.id,
                title=f"Discovery call #{i + 1}",
                start_time=start,
                end_time=start + timedelta(minutes=30),
                meeting_timezone=host.timezone,
                status="scheduled" if i % 4 else "completed",
            )
            db.add(m)
            db.flush()
            db.add(MeetingInvitee(meeting_id=m.id, contact_id=contacts[i % len(contacts)].id))

        for u in users:
            for wd in range(0, 5):
                db.add(AvailabilitySlot(user_id=u.id, weekday=wd, start="09:00", end="17:00"))

        db.commit()
        print(f"Seeded team={team.name} users={len(users)} contacts={len(contacts)} meetings=12")
    finally:
        db.close()


if __name__ == "__main__":
    run()
