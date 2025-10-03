from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.models.public import BasePublic as Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Escalation(Base):
    __tablename__ = "escalations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(String, nullable=False)   # e.g. Low, Medium, High
    status = Column(String, default="Open")     # Open, In Progress, Resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
