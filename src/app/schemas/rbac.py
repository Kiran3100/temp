from enum import Enum
from pydantic import BaseModel
from typing import List


class RoleEnum(str, Enum):
    super_admin = "super_admin"
    admin = "admin"


# Each role maps to allowed permissions
ROLE_PERMISSIONS = {
    RoleEnum.super_admin: {
        "add_admin",
        "add_tenant",
        "add_hostel",
        "add_floor",
        "add_room",
        "add_bed",
    },
    RoleEnum.admin: {
        "add_tenant",
        "add_hostel",
        "add_floor",
        "add_room",
        "add_bed",
    },
}


class UserRole(BaseModel):
    role: RoleEnum
    permissions: List[str]

    class Config:
        orm_mode = True