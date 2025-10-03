from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import helpdesk
from app.schemas import helpdesk
from app.db.session import get_db

router = APIRouter(
    prefix="/users",
    tags=["helpdesk Users"]
)


# ✅ Create a new user
@router.post("/", response_model=helpdesk.UserOut)
def create_user(user: helpdesk.UserCreate, db: Session = Depends(get_db)):
    # check if email already exists
    existing_user = db.query(helpdesk.User).filter(helpdesk.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = helpdesk.User(
        username=user.username,
        email=user.email,
        password=user.password  # ⚠️ plain text for now (can add hashing later)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ✅ List all users
@router.get("/", response_model=list[helpdesk.UserOut])
def list_users(db: Session = Depends(get_db)):
    users = db.query(helpdesk.User).all()
    return users


# ✅ Get a single user by ID
@router.get("/{user_id}", response_model=helpdesk.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(helpdesk.User).filter(helpdesk.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
