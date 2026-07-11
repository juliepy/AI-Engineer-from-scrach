"""Manual end-to-end smoke check against a running Schedulr API (port 8000).

Verifies auth (JWT + legacy session), meetings, teams, contacts, export, and
demonstrates the planted SCH-203 timezone bug. Never prints credentials.

Run:  uv run python e2e_check.py
"""
import httpx
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Meeting, User
from app.utils.timezones import TimezoneAwareTime

BASE = "http://localhost:8000"


def main() -> None:
    c = httpx.Client(base_url=BASE, timeout=10)

    # health
    assert c.get("/health").json()["status"] == "ok"
    print("[ok] /health")

    # JWT login as Lukas (Europe/Berlin)
    r = c.post("/api/auth/login", data={"username": "lukas@acme.test", "password": "password123"})
    r.raise_for_status()
    jwt = r.json()["access_token"]
    hdr = {"Authorization": f"Bearer {jwt}"}

    me = c.get("/api/auth/me", headers=hdr).json()
    print(f"[ok] /api/auth/me -> {me['email']} tz={me['timezone']}")

    meetings = c.get("/api/meetings", headers=hdr).json()
    print(f"[ok] /api/meetings -> {len(meetings)} rows; first start='{meetings[0]['start']}'")

    team = c.get("/api/teams/me", headers=hdr).json()
    print(f"[ok] /api/teams/me -> {team['name']} ({len(team['members'])} members)")

    exp = c.get("/api/meetings/export", headers=hdr, params={"format": "pdf"})
    print(f"[ok] /api/meetings/export?format=pdf -> {exp.status_code} {len(exp.content)} bytes")
    bad = c.get("/api/meetings/export", headers=hdr, params={"format": "csv"})
    print(f"[ok] csv export not supported yet (SCH-142 adds it) -> {bad.status_code}")

    # legacy session auth path (contacts)
    s = c.post("/api/auth/legacy-login", data={"username": "dana@acme.test", "password": "password123"})
    sess = s.json()["session_token"]
    contacts = c.get("/api/contacts", headers={"X-Session-Token": sess}).json()
    print(f"[ok] /api/contacts (legacy session auth) -> {len(contacts)} contacts")

    # --- demonstrate the SCH-203 timezone bug ---
    db = SessionLocal()
    try:
        m = db.execute(select(Meeting).order_by(Meeting.start_time)).scalars().first()
        lukas = db.execute(select(User).where(User.email == "lukas@acme.test")).scalar_one()
        api_start = next(x for x in meetings if x["id"] == m.id)["start"]
        correct = TimezoneAwareTime(m.start_time).render(lukas.timezone, "%Y-%m-%d %H:%M")
        utc_naive = m.start_time.strftime("%Y-%m-%d %H:%M")
        print("\n--- SCH-203 timezone bug (viewer = Lukas, Europe/Berlin) ---")
        print(f"  stored UTC          : {utc_naive}")
        print(f"  API returns (buggy) : {api_start}   <- naive UTC, ignores viewer tz")
        print(f"  CORRECT for Berlin  : {correct}")
        if api_start == utc_naive and correct != utc_naive:
            print("  RESULT: BUG CONFIRMED — Berlin user sees UTC time, off by the offset.")
        else:
            print("  RESULT: bug not reproduced (unexpected).")
    finally:
        db.close()

    print("\nALL ENDPOINTS OK")


if __name__ == "__main__":
    main()
