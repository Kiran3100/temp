from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import pyotp
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from typing import Optional
from app.schemas.user import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2FA helpers
def generate_2fa_secret() -> str:
    return pyotp.random_base32()

def get_2fa_code(secret: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_2fa_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code)

async def create_user(
    db: AsyncSession, 
    username: str,
    email: str, 
    password: str, 
    mobile_number: str,
    full_name: Optional[str] = None, 
    roles: list[str] | None = None,
    hostel_id: Optional[int] = None
) -> User:
    roles = roles or [Role.tenant.value]
    user = User(
        username=username,
        email=email, 
        full_name=full_name, 
        mobile_number=mobile_number,
        hashed_password=get_password_hash(password), 
        roles=roles,
        hostel_id=hostel_id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    q = await db.execute(select(User).where(User.email == email))
    user = q.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_token_for_user(user: User):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "roles": user.roles,
    }
    if user.hostel_id:
        payload["hostel_id"] = user.hostel_id
    return create_access_token(subject=user.id, roles=user.roles, extra=payload)