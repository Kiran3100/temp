# src/app/schemas/room.py
from pydantic import BaseModel
from typing import Optional

class RoomCreate(BaseModel):
    floor_id: int
    number: str
    capacity: int = 4

class RoomOut(BaseModel):
    id: int
    floor_id: int
    number: str
    capacity: int

    class Config:
        orm_mode = True
