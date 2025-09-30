# src/app/models/user.py
from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base

BasePublic = declarative_base()


class User(BasePublic):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(JSON, default=list)  # ["super_admin"], ["hostel_admin"], ["tenant"]
    is_active = Column(Boolean, default=True)
    hostel_id = Column(Integer, nullable=True)  # links hostel_admins/tenants to a hostel
    created_at = Column(DateTime, default=func.now())