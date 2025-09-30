from pydantic import BaseModel, ConfigDict
from typing import Optional

class RoomCreate(BaseModel):
    floor_id: int
    number: str
    capacity: int = 4

class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    floor_id: int
    number: str
    capacity: int
