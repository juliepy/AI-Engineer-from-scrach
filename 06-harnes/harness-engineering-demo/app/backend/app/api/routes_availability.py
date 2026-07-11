"""Availability routes.

Wires the orphaned AvailabilitySlot model with full CRUD.
Uses JWT auth (consistent with meetings/teams routes).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AvailabilitySlot, User
from app.schemas.availability import (
    AvailabilitySlotCreate,
    AvailabilitySlotOut,
    AvailabilityBulkSet,
)
from app.services.auth_jwt import get_current_user

router = APIRouter(prefix="/api/availability", tags=["availability"])


@router.get("")
def get_my_availability(
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AvailabilitySlotOut]:
    rows = (
        db.execute(
            select(AvailabilitySlot)
            .where(AvailabilitySlot.user_id == current.id)
            .order_by(AvailabilitySlot.weekday)
        )
        .scalars()
        .all()
    )
    return [AvailabilitySlotOut.model_validate(r) for r in rows]


@router.get("/user/{user_id}")
def get_user_availability(
    user_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AvailabilitySlotOut]:
    """Get availability for any team member."""
    from app.models import User as UserModel
    target = db.execute(
        select(UserModel).where(UserModel.id == user_id, UserModel.team_id == current.team_id)
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    rows = (
        db.execute(
            select(AvailabilitySlot)
            .where(AvailabilitySlot.user_id == user_id)
            .order_by(AvailabilitySlot.weekday)
        )
        .scalars()
        .all()
    )
    return [AvailabilitySlotOut.model_validate(r) for r in rows]


@router.post("", status_code=201)
def add_slot(
    payload: AvailabilitySlotCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AvailabilitySlotOut:
    slot = AvailabilitySlot(
        user_id=current.id,
        weekday=payload.weekday,
        start=payload.start,
        end=payload.end,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return AvailabilitySlotOut.model_validate(slot)


@router.put("")
def set_availability(
    payload: AvailabilityBulkSet,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AvailabilitySlotOut]:
    """Replace all availability slots for the current user."""
    existing = db.execute(
        select(AvailabilitySlot).where(AvailabilitySlot.user_id == current.id)
    ).scalars().all()
    for slot in existing:
        db.delete(slot)
    db.flush()

    new_slots = []
    for s in payload.slots:
        slot = AvailabilitySlot(
            user_id=current.id,
            weekday=s.weekday,
            start=s.start,
            end=s.end,
        )
        db.add(slot)
        new_slots.append(slot)
    db.commit()
    for slot in new_slots:
        db.refresh(slot)
    return [AvailabilitySlotOut.model_validate(s) for s in new_slots]


@router.delete("/{slot_id}", status_code=204)
def delete_slot(
    slot_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    slot = db.execute(
        select(AvailabilitySlot).where(
            AvailabilitySlot.id == slot_id,
            AvailabilitySlot.user_id == current.id,
        )
    ).scalar_one_or_none()
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    db.delete(slot)
    db.commit()
