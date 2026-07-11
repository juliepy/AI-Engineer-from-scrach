from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Team, User
from app.schemas.team import TeamOut, TeamMemberOut, InviteMember, UpdateMemberRole
from app.services.auth_jwt import get_current_user
from app.services.security import hash_password

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("/me")
def my_team(current: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TeamOut:
    team = db.get(Team, current.team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    members = (
        db.execute(select(User).where(User.team_id == current.team_id).order_by(User.full_name))
        .scalars()
        .all()
    )
    return TeamOut(
        id=team.id,
        name=team.name,
        slug=team.slug,
        members=[
            TeamMemberOut(
                id=u.id,
                name=u.full_name,
                email=u.email,
                timezone=u.timezone,
                role=u.role,
            )
            for u in members
        ],
    )


@router.post("/me/members", status_code=201)
def invite_member(
    payload: InviteMember,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TeamMemberOut:
    """Invite (create) a new team member. Admin only."""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    # Check no duplicate email in team
    existing = db.execute(
        select(User).where(User.email == payload.email)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already in use")
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        timezone=payload.timezone,
        team_id=current.team_id,
        hashed_password=hash_password("changeme123"),  # demo: temp password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TeamMemberOut(
        id=user.id,
        name=user.full_name,
        email=user.email,
        timezone=user.timezone,
        role=user.role,
    )


@router.patch("/me/members/{user_id}/role")
def update_member_role(
    user_id: int,
    payload: UpdateMemberRole,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TeamMemberOut:
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    user = db.execute(
        select(User).where(User.id == user_id, User.team_id == current.team_id)
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Member not found")
    valid_roles = {"admin", "member"}
    if payload.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role must be one of {valid_roles}")
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return TeamMemberOut(
        id=user.id,
        name=user.full_name,
        email=user.email,
        timezone=user.timezone,
        role=user.role,
    )


@router.delete("/me/members/{user_id}", status_code=204)
def remove_member(
    user_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    user = db.execute(
        select(User).where(User.id == user_id, User.team_id == current.team_id)
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(user)
    db.commit()
