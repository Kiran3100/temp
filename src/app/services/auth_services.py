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

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(subject: str, data: dict = {}, expires_delta: int | None = None):
    to_encode = {"sub": subject, **data}
    expire = datetime.utcnow() + timedelta(minutes=(expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except Exception as e:
        raise

# 2FA helpers
def generate_2fa_secret() -> str:
    return pyotp.random_base32()

def get_2fa_code(secret: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.now()

def verify_2fa_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code)

async def create_user(db: AsyncSession, email: str, password: str, full_name: Optional[str] = None, roles: list[str] | None = None) -> User:
    roles = roles or [Role.tenant.value]
    user = User(email=email, full_name=full_name, hashed_password=get_password_hash(password), roles=roles)
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


def create_token_for_user(user: User) -> str:
    """
    Include hostel_id claim for hostel_admin and tenant roles.
    """
    payload = {
        "sub": str(user.id),
        "roles": user.roles,
    }
    if "hostel_admin" in user.roles or "tenant" in user.roles:
        payload["hostel_id"] = user.hostel_id
    return create_access_token(subject=user.id, roles=user.roles, expires_delta=None, extra=payload)

def create_token_for_user(user: User) -> str:
    """
    Include hostel_id claim for hostel_admin and tenant roles.
    """
    payload = {
        "sub": str(user.id),
        "roles": user.roles,
    }
    if "hostel_admin" in user.roles or "tenant" in user.roles:
        payload["hostel_id"] = user.hostel_id
    return create_access_token(subject=user.id, roles=user.roles, expires_delta=None, extra=payload)