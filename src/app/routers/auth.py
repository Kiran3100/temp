from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, Token
from app.dependencies.auth import oauth2_scheme, require_roles  # Add require_roles import
from app.db.session import get_public_db
from app.services.auth_services import create_user, authenticate_user, create_token_for_user
from app.schemas.user import Role
from app.models.user import User as UserModel
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(payload: UserCreate, db=Depends(get_public_db)):
    async with db as session:
        # Check if username already exists
        existing_username = await session.execute(
            UserModel.__table__.select().where(UserModel.username == payload.username)
        )
        if existing_username.scalars().first():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = await session.execute(
            UserModel.__table__.select().where(UserModel.email == payload.email)
        )
        if existing_email.scalars().first():
            raise HTTPException(status_code=400, detail="Email already exists")

        user = await create_user(
            session,
            username=payload.username,
            email=payload.email,
            password=payload.password,
            mobile_number=payload.mobile_number,
            full_name=payload.full_name,
            roles=[r.value for r in payload.roles],
            hostel_id=payload.hostel_id,
        )
        
        token = create_token_for_user(user_id=user.id, roles=user.roles)
        return {"access_token": token, "token_type": "bearer"}


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_public_db)):
    async with db as session:
        user = await authenticate_user(session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        # token now carries hostel_id claim automatically
        token = create_token_for_user(user)
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
async def me(user=Depends(require_roles("tenant", "hostel_admin", "super_admin"))):
    return user