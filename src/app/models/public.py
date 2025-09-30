# src/app/models/public.py
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

BasePublic = declarative_base()


class User(BasePublic):
    """
    Public schema user table - stores all users (super_admin, hostel_admin, tenant)
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    roles = Column(JSON, default=list)  # ["super_admin"], ["hostel_admin"], ["tenant"]
    is_active = Column(Boolean, default=True)
    hostel_id = Column(Integer, nullable=True)  # links hostel_admins/tenants to a hostel
    two_fa_enabled = Column(Boolean, default=False)
    two_fa_secret = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)


class PublicHostel(BasePublic):
    """
    Public schema hostel registry - one entry per hostel/tenant
    """
    __tablename__ = "hostels"
    __table_args__ = {"schema": "public"}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)  # Use metadata_ to avoid Python keyword
    created_at = Column(DateTime, default=func.now(), nullable=False)