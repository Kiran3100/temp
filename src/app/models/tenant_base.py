from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime

TenantBase = declarative_base()

class Hostel(TenantBase):
    __tablename__ = "hostels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Floor(TenantBase):
    __tablename__ = "floors"
    id = Column(Integer, primary_key=True)
    hostel_id = Column(Integer, nullable=False)  # redundant if per-schema, but helpful
    name = Column(String)

class Room(TenantBase):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True)
    floor_id = Column(Integer, nullable=False)
    number = Column(String)

class Bed(TenantBase):
    __tablename__ = "beds"
    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, nullable=False)
    bed_no = Column(String)
    occupied = Column(Boolean, default=False)

class TenantProfile(TenantBase):
    __tablename__ = "tenant_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    bed_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)
