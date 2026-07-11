from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import TokenResponse, UserOut, ProfileUpdate, PasswordChange
from app.services.auth_jwt import create_access_token, get_current_user
from app.services.auth_legacy import issue_session
from app.services.security import verify_password, hash_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 form uses "username" — we treat it as email
    user = db.execute(select(User).where(User.email == form.username)).scalar_one_or_none()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return TokenResponse(access_token=create_access_token(user.id))


# The old endpoint that the JWT migration never removed. Still works.
@router.post("/legacy-login")
def legacy_login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == form.username)).scalar_one_or_none()
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"session_token": issue_session(user.id)}


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


@router.patch("/me/profile", response_model=UserOut)
def update_profile(
    payload: ProfileUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        current.full_name = payload.full_name
    if payload.timezone is not None:
        current.timezone = payload.timezone
    db.add(current)
    db.commit()
    db.refresh(current)
    return current


@router.post("/me/change-password", status_code=204)
def change_password(
    payload: PasswordChange,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current.hashed_password = hash_password(payload.new_password)
    db.add(current)
    db.commit()
