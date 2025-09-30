from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from enum import Enum

class Role(str, Enum):
    super_admin = "super_admin"
    hostel_admin = "hostel_admin"
    tenant = "tenant"

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str]
    roles: List[Role] = [Role.tenant]

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    full_name: Optional[str]
    roles: List[Role]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"