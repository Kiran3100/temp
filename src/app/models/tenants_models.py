from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.public import BasePublic as Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    room = Column(String, nullable=False)
    payments = relationship("Payment", back_populates="user")
    dashboard_id = Column(Integer, ForeignKey("dashboard.id"))
    dashboard = relationship("Dashboard", uselist=False, back_populates="profiles")



class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("profiles.id"), nullable=False)
    status = Column(String, default="Pending")
    amount = Column(Float, nullable=False)
    paid_on = Column(DateTime(timezone=True), server_default=func.now())  # ✅ DB default timestamp

    user = relationship("Profile", back_populates="payments")


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # ✅ DB default timestamp

class Dashboard(Base):
    __tablename__ = "dashboard"

    id = Column(Integer, primary_key=True, index=True)
    total_profiles = Column(Integer, default=0)
    total_payments = Column(Float, default=0.0)
    total_paid_amount = Column(Float, default=0.0)
    recent_payments = Column(String)  # Comma-separated payment IDs for simplicity
    notices_count = Column(Integer, default=0)  # Count of notices
    profiles = relationship("Profile", back_populates="dashboard")
    
    
class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    mobile = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    address = Column(String, nullable=False)
    profession = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    pan = Column(String, nullable=False, unique=True)
    aadhar = Column(String, nullable=False, unique=True)
    room_number = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)  # ⚠️ Hash in real apps
    pan_pic = Column(String, nullable=True)
    aadhar_pic = Column(String, nullable=True)