from pydantic import BaseModel


class TeamMemberOut(BaseModel):
    id: int
    name: str
    email: str
    timezone: str
    role: str

    class Config:
        from_attributes = True


class TeamOut(BaseModel):
    id: int
    name: str
    slug: str
    members: list[TeamMemberOut]


class InviteMember(BaseModel):
    email: str
    full_name: str
    role: str = "member"
    timezone: str = "UTC"


class UpdateMemberRole(BaseModel):
    role: str  # "admin" | "member"
