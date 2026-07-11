from datetime import datetime

from pydantic import BaseModel


class ContactCreate(BaseModel):
    name: str
    email: str
    company: str | None = None
    phone: str | None = None
    title: str | None = None
    notes: str | None = None
    stage: str = "lead"


class ContactUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    company: str | None = None
    phone: str | None = None
    title: str | None = None
    notes: str | None = None
    stage: str | None = None


class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    company: str | None
    phone: str | None
    title: str | None
    notes: str | None
    stage: str
    created_at: datetime

    class Config:
        from_attributes = True
