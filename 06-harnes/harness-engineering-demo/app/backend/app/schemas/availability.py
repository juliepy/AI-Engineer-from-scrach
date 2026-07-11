from pydantic import BaseModel


class AvailabilitySlotCreate(BaseModel):
    weekday: int  # 0=Mon ... 6=Sun
    start: str   # "HH:MM"
    end: str     # "HH:MM"


class AvailabilitySlotUpdate(BaseModel):
    start: str | None = None
    end: str | None = None


class AvailabilitySlotOut(BaseModel):
    id: int
    user_id: int
    weekday: int
    start: str
    end: str

    class Config:
        from_attributes = True


class AvailabilityBulkSet(BaseModel):
    """Replace all availability slots for the current user."""
    slots: list[AvailabilitySlotCreate]
