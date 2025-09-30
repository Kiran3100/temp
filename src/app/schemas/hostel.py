# src/app/schemas/hostel.py
from pydantic import BaseModel, Field
from typing import Optional


class HostelCreate(BaseModel):
    name: str = Field(..., example="Greenfield Hostel")
    address: Optional[str] = Field(None, example="123, Campus Road")


class HostelOut(BaseModel):
    id: int
    name: str
    address: Optional[str]

    class Config:
        orm_mode = True
