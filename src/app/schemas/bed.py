# src/app/schemas/bed.py
from pydantic import BaseModel
from typing import Optional

class BedCreate(BaseModel):
    room_id: int
    bed_no: str

class BedAssign(BaseModel):
    tenant_id: int

class BedOut(BaseModel):
    id: int
    room_id: int
    bed_no: str
    occupied: bool
    tenant_id: Optional[int]

    class Config:
        orm_mode = True
