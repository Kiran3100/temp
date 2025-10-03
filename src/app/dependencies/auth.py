from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from app.core.security import decode_token  # import decode_token from security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token"
        )
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    if "sub" not in payload or "roles" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    return {
        "id": int(payload["sub"]),
        "username": payload.get("username"),
        "roles": payload.get("roles", []),
        "hostel_id": payload.get("hostel_id"),
    }


def require_roles(*allowed_roles: str):
    def checker(current_user=Depends(get_current_user)):
        if not any(r in current_user["roles"] for r in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role"
            )
        return current_user
    return checker


def get_current_tenant_user(request: Request, current_user=Depends(get_current_user)):
    hostel_id_header = request.headers.get("X-Hostel-ID")
    if not hostel_id_header:
        raise HTTPException(
            status_code=400,
            detail="X-Hostel-ID header required"
        )
    tenant_schema = f"hostel_{hostel_id_header}"
    roles = current_user["roles"]

    if "super_admin" in roles:
        return {"user": current_user, "tenant_schema": tenant_schema}

    if "hostel_admin" in roles:
        if str(current_user.get("hostel_id")) != hostel_id_header:
            raise HTTPException(
                status_code=403,
                detail="Cannot access another hostel's resources"
            )
        return {"user": current_user, "tenant_schema": tenant_schema}

    if "tenant" in roles:
        if str(current_user.get("hostel_id")) != hostel_id_header:
            raise HTTPException(
                status_code=403,
                detail="Tenant cannot access another hostel"
            )
        return {"user": current_user, "tenant_schema": tenant_schema}

    raise HTTPException(status_code=403, detail="Unknown role")
