from fastapi import Depends, HTTPException, status
from app.schemas.rbac import ROLE_PERMISSIONS, RoleEnum
from app.dependencies.auth import get_current_user  # your JWT auth dependency


def require_permission(permission: str):
    def wrapper(current_user=Depends(get_current_user)):
        # Assume current_user["roles"] is a list of RoleEnum
        for role in current_user["roles"]:
            if permission in ROLE_PERMISSIONS[role]:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' denied",
        )
    return wrapper