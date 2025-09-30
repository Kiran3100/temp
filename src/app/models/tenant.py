# src/app/models/tenant.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

TenantBase = declarative_base()

class Floor(TenantBase):
    __tablename__ = "floors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Room(TenantBase):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(Integer, nullable=False)
    number = Column(String, nullable=False, index=True)
    capacity = Column(Integer, default=4)
    created_at = Column(DateTime, default=func.now())

class Bed(TenantBase):
    __tablename__ = "beds"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, nullable=False)
    bed_no = Column(String, nullable=False)
    occupied = Column(Boolean, default=False)
    tenant_id = Column(Integer, nullable=True)  # reference to user id in public or tenant-profile
    created_at = Column(DateTime, default=func.now())

class Invoice(TenantBase):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(20), default="pending")  # pending, paid, failed
    external_payment_id = Column(String, nullable=True)
    _metadata = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
