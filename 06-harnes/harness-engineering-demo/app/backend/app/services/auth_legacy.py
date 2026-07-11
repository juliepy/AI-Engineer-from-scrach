"""Legacy session-token auth — the *older* pattern, still in use on some routes.

This predates the JWT migration that never finished. It keeps an in-process
dict of opaque tokens. Real production used Redis; this is the leftover shape.
Two auth systems coexisting is one of the intentional smells.

# TODO: refactor — finish the JWT migration and delete this (filed ~2 years ago)
"""
import secrets

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

# in-memory token store: token -> user_id
_SESSIONS: dict[str, int] = {}


def issue_session(user_id: int) -> str:
    tok = secrets.token_hex(24)
    _SESSIONS[tok] = user_id
    return tok


def resolve_session(token: str) -> int | None:
    return _SESSIONS.get(token)


def get_user_from_session(
    x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
    db: Session = Depends(get_db),
) -> User:
    if not x_session_token:
        raise HTTPException(status_code=401, detail="Missing session token")
    uid = resolve_session(x_session_token)
    if uid is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    user = db.execute(select(User).where(User.id == uid)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid session token")
    return user
