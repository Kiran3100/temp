from pydantic import BaseModel, EmailStr
from datetime import datetime


# ---------- User Schemas ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes  = True


# ---------- Escalation Schemas ----------
class EscalationBase(BaseModel):
    title: str
    description: str
    priority: str
    status: str = "Open"


class EscalationCreate(EscalationBase):
    pass


class EscalationOut(EscalationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
