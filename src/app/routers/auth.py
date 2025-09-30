# src/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, Token
from app.dependencies.auth import oauth2_scheme
from app.db.session import get_public_db
from app.services.auth_service import create_user, authenticate_user, create_token_for_user
from app.schemas.user import Role
from app.models.user import User as UserModel
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

    
@router.post("/register", response_model=Token)
async def register(payload: UserCreate, db=Depends(get_public_db)):
    async with db as session:
        existing = await session.execute(UserModel.__table__.select().where(UserModel.email == payload.email))
        if existing.scalars().first():
            raise HTTPException(status_code=400, detail="User already exists")

        user = await create_user(
            session,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            roles=[r.value for r in payload.roles],
        )
        # include hostel_id if one exists in metadata (for hostel_admin/tenant accounts)
        token = create_token_for_user(user_id=user.id, roles=user.roles)
        return {"access_token": token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_public_db)):
    async with db as session:
        user = await authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        # For hostel_admin or tenant, include hostel_id in token claims (example: user.hostel_id column if present)
        token = create_token_for_user(user_id=user.id, roles=user.roles)
        return {"access_token": token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh(current_token: str = Depends(oauth2_scheme)):
    """
    Refresh the token: validate existing token and emit a new one with new exp.
    """
    from app.core.security import decode_token
    try:
        payload = decode_token(current_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    roles = payload.get("roles", [])
    new_token = create_token_for_user(user_id=user_id, roles=roles)
    return {"access_token": new_token, "token_type": "bearer"}

@router.get("/me")
def me(user=Depends(require_roles("tenant","hostel_admin","super_admin"))):
    return user