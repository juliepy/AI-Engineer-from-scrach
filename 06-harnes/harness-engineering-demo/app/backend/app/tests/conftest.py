"""Test fixtures for Schedulr backend.

Uses a real Postgres test database (schedulr_test) with transaction-rollback
isolation — each test gets a clean slate via nested transactions.
"""
import os
from collections.abc import Generator
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Team, User, Meeting, MeetingInvitee, Contact, AvailabilitySlot
from app.services.security import hash_password
from app.services.auth_jwt import create_access_token
from app.services.auth_legacy import issue_session

# ── Database setup ─────────────────────────────────────────────────────────────
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://schedulr:schedulr@localhost:5433/schedulr_test",
)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True, future=True)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> Generator[None, None, None]:
    """Create all tables once per session."""
    Base.metadata.create_all(test_engine)
    yield
    Base.metadata.drop_all(test_engine)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    """Each test gets a transaction that is rolled back afterward."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)  # type: ignore[call-overload]

    # Savepoint so nested transactions work correctly inside the test
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess: Session, trans: "object") -> None:  # type: ignore[type-arg]
        from sqlalchemy.orm.session import SessionTransaction
        t: SessionTransaction = trans  # type: ignore[assignment]
        if t.nested and not t._parent.nested:  # type: ignore[union-attr]
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    """TestClient with the test DB injected."""
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Seed helpers ───────────────────────────────────────────────────────────────

@pytest.fixture()
def team(db: Session) -> Team:
    t = Team(name="Test Team", slug="test-team")
    db.add(t)
    db.flush()
    return t


@pytest.fixture()
def admin_user(team: Team, db: Session) -> User:
    u = User(
        email="admin@test.test",
        full_name="Admin User",
        timezone="UTC",
        role="admin",
        team_id=team.id,
        hashed_password=hash_password("password123"),
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def member_user(team: Team, db: Session) -> User:
    u = User(
        email="member@test.test",
        full_name="Member User",
        timezone="Europe/Berlin",
        role="member",
        team_id=team.id,
        hashed_password=hash_password("password123"),
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def admin_token(admin_user: User) -> str:
    return create_access_token(admin_user.id)


@pytest.fixture()
def member_token(member_user: User) -> str:
    return create_access_token(member_user.id)


@pytest.fixture()
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def member_headers(member_token: str) -> dict:
    return {"Authorization": f"Bearer {member_token}"}


@pytest.fixture()
def admin_session_headers(admin_user: User) -> dict:
    tok = issue_session(admin_user.id)
    return {"X-Session-Token": tok}


@pytest.fixture()
def contact(team: Team, db: Session) -> Contact:
    c = Contact(
        team_id=team.id,
        name="Priya Shah",
        email="priya@globex.test",
        company="Globex",
        stage="opportunity",
    )
    db.add(c)
    db.flush()
    return c


@pytest.fixture()
def meeting(team: Team, admin_user: User, contact: Contact, db: Session) -> Meeting:
    start = datetime(2026, 7, 20, 14, 0, tzinfo=timezone.utc)
    m = Meeting(
        team_id=team.id,
        host_id=admin_user.id,
        title="Discovery Call",
        start_time=start,
        end_time=start + timedelta(minutes=30),
        meeting_timezone="UTC",
        status="scheduled",
    )
    db.add(m)
    db.flush()
    db.add(MeetingInvitee(meeting_id=m.id, contact_id=contact.id))
    db.flush()
    return m


@pytest.fixture()
def availability_slot(admin_user: User, db: Session) -> AvailabilitySlot:
    slot = AvailabilitySlot(user_id=admin_user.id, weekday=0, start="09:00", end="17:00")
    db.add(slot)
    db.flush()
    return slot
