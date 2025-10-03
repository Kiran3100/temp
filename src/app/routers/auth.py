from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, Token
from app.dependencies.auth import oauth2_scheme, require_roles  # Add require_roles import
from app.db.session import get_public_db
from app.services.auth_services import create_user, authenticate_user, create_token_for_user
from app.schemas.user import Role
from app.models.user import User as UserModel
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_
from app.core.security import verify_password

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
        # Try both username and email for flexibility
        from sqlalchemy import or_
        q = await session.execute(
            select(UserModel).where(
                or_(
                    UserModel.username == form_data.username,
                    UserModel.email == form_data.username
                )
            )
        )
        user = q.scalars().first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )
        
        token = create_token_for_user(user)
        return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh(current_token: str = Depends(oauth2_scheme), db=Depends(get_public_db)):
    from app.core.security import decode_token
    try:
        payload = decode_token(current_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user_id = int(payload.get("sub"))
    
    # Fetch fresh user data from DB
    async with db as session:
        q = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = q.scalars().first()
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    
    new_token = create_token_for_user(user)
    return {"access_token": new_token, "token_type": "bearer"}


@router.get("/me")
async def me(user=Depends(require_roles("tenant", "hostel_admin", "super_admin"))):
    return user