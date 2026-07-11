"""Contacts routes.

Smell: these still authenticate with the *legacy session token* (X-Session-Token
header) while the meetings/auth routes use JWT. Same app, two auth systems.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Contact, User
from app.schemas.contact import ContactCreate, ContactUpdate, ContactOut
from app.services.auth_legacy import get_user_from_session

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("")
def get_contacts(
    current: User = Depends(get_user_from_session),
    db: Session = Depends(get_db),
) -> list[ContactOut]:
    rows = (
        db.execute(select(Contact).where(Contact.team_id == current.team_id).order_by(Contact.name))
        .scalars()
        .all()
    )
    return [ContactOut.model_validate(c) for c in rows]


@router.post("", status_code=201)
def create_contact(
    payload: ContactCreate,
    current: User = Depends(get_user_from_session),
    db: Session = Depends(get_db),
) -> ContactOut:
    c = Contact(
        team_id=current.team_id,
        name=payload.name,
        email=payload.email,
        company=payload.company,
        phone=payload.phone,
        title=payload.title,
        notes=payload.notes,
        stage=payload.stage,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return ContactOut.model_validate(c)


@router.get("/{contact_id}")
def get_contact(
    contact_id: int,
    current: User = Depends(get_user_from_session),
    db: Session = Depends(get_db),
) -> ContactOut:
    c = db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.team_id == current.team_id)
    ).scalar_one_or_none()
    if c is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactOut.model_validate(c)


@router.patch("/{contact_id}")
def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    current: User = Depends(get_user_from_session),
    db: Session = Depends(get_db),
) -> ContactOut:
    c = db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.team_id == current.team_id)
    ).scalar_one_or_none()
    if c is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    if payload.name is not None:
        c.name = payload.name
    if payload.email is not None:
        c.email = payload.email
    if payload.company is not None:
        c.company = payload.company
    if payload.phone is not None:
        c.phone = payload.phone
    if payload.title is not None:
        c.title = payload.title
    if payload.notes is not None:
        c.notes = payload.notes
    if payload.stage is not None:
        c.stage = payload.stage
    db.commit()
    db.refresh(c)
    return ContactOut.model_validate(c)


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    current: User = Depends(get_user_from_session),
    db: Session = Depends(get_db),
) -> None:
    c = db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.team_id == current.team_id)
    ).scalar_one_or_none()
    if c is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(c)
    db.commit()
