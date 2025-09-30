from pydantic import BaseModel, ConfigDict
from typing import Optional

class BedCreate(BaseModel):
    room_id: int
    bed_no: str

class BedAssign(BaseModel):
    tenant_id: int

class BedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    room_id: int
    bed_no: str
    occupied: bool
    tenant_id: Optional[int]