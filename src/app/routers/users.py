from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.models.user import User
from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.schemas.user import UserOut
from typing import List

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user=Depends(get_current_user), db=Depends(get_db)):
    """Get current user's information"""
    async with db as session:
        q = await session.execute(select(User).where(User.id == current_user["id"]))
        user = q.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@router.get("/", response_model=List[UserOut], dependencies=[Depends(require_roles("super_admin"))])
async def list_users(db=Depends(get_db)):
    """List all users (super_admin only)"""
    async with db as session:
        q = await session.execute(select(User).order_by(User.id))
        users = q.scalars().all()
        return users


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("super_admin", "hostel_admin"))])
async def get_user(user_id: int, db=Depends(get_db)):
    """Get a specific user by ID"""
    async with db as session:
        q = await session.execute(select(User).where(User.id == user_id))
        user = q.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user