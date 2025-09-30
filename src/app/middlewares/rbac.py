from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_services import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    # payload should include user_id and roles
    return payload

def require_roles(*allowed_roles):
    def role_checker(current_user=Depends(get_current_user)):
        roles = current_user.get("roles", [])
        if not any(r in roles for r in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user
    return role_checker
