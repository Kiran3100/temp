from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class HostelCreate(BaseModel):
    name: str = Field(..., example="Greenfield Hostel")
    address: Optional[str] = Field(None, example="123, Campus Road")

class HostelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    address: Optional[str]
