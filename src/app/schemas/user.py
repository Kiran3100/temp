from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import List, Optional
from enum import Enum

class Role(str, Enum):
    super_admin = "super_admin"
    hostel_admin = "hostel_admin"
    tenant = "tenant"
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)
    mobile_number: str = Field(..., min_length=10, max_length=15)
    full_name: Optional[str] = None
    roles: List[Role] = [Role.tenant]
    hostel_id: Optional[int] = None
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    mobile_number: str
    roles: List[str]  # Changed from List[Role] to List[str]
    hostel_id: Optional[int]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"