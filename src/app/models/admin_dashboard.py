from sqlalchemy import Column, Integer, String, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# ---------------- Complaints ----------------
class ComplaintStatus(str, enum.Enum):
    Pending = "Pending"
    InProgress = "In Progress"
    Resolved = "Resolved"

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.Pending, nullable=False)
    assigned_to = Column(String, nullable=True)


# ---------------- Notices ----------------
class Notice(Base):
    __tablename__ = "notices"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)


# ---------------- Occupancy (simplified for dashboard) ----------------
class OccupancyStatus(str, enum.Enum):
    Vacant = "Vacant"
    Occupied = "Occupied"

class Occupancy(Base):
    __tablename__ = "occupancy"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, nullable=False)
    status = Column(Enum(OccupancyStatus), default=OccupancyStatus.Vacant, nullable=False)


# ---------------- Fee Collection ----------------
class FeeStatus(str, enum.Enum):
    Paid = "Paid"
    Pending = "Pending"
    Unpaid = "Unpaid"
    Partial = "Partial"

class FeeCollection(Base):
    __tablename__ = "feecollection"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String, nullable=False)
    status = Column(Enum(FeeStatus), default=FeeStatus.Unpaid, nullable=False)

class Dashboard(Base):
    __tablename__ = "dashboard"
    id = Column(Integer, primary_key=True, index=True)
    occupancy_percent = Column(Float, nullable=False, default=0.0)
    fee_collection = Column(Float, nullable=False, default=0.0)
    complaints = Column(Integer, nullable=False, default=0)
    notice = Column(String, nullable=True, default="")

