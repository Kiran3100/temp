from pydantic import BaseModel , EmailStr
from typing import Optional
from datetime import datetime

class TenantBase(BaseModel):
    first_name: str
    last_name: str
    mobile: str
    email: EmailStr
    address: str
    profession: str
    gender: str
    pan: str
    aadhar: str
    room_number: str
    username: str
    password: str   # in production hash this

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    id: int
    pan_pic: str | None = None
    aadhar_pic: str | None = None

    class Config:
        from_attributes = True

# ---------- Dashboard Summary ----------
class Dashboard(BaseModel):
    total_profiles: int
    total_payments: int
    total_paid_amount: float
    recent_payments: list['Payment']
    notices: list['Notice']
    class Config:
        from_attributes = True


# ---------- Profile ----------
class ProfileBase(BaseModel):
    name: str
    room: str
    email: str


class ProfileCreate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: int

    class Config:
        from_attributes = True  # ✅ replaces orm_mode in Pydantic v2


# ---------- Payments ----------
class PaymentBase(BaseModel):
    status: str
    amount: float
    

class PaymentCreate(PaymentBase):
    user_id: int
    status: str
    amount: float

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    status: Optional[str] = None

class Payment(PaymentBase):
    id: int 
    paid_on: datetime

    class Config:
        from_attributes = True
# ---------- Notices ----------
class NoticeBase(BaseModel):
    title: str
    description: str
    created_at: datetime
class NoticeCreate(NoticeBase):
    title: str
    description: str
class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
class Notice(NoticeBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

