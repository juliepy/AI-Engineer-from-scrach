from pydantic import BaseModel


class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None
