from pydantic import BaseModel
from enum import Enum
from typing import Optional

# ---------------- Enum Classes ----------------
class ComplaintStatus(str, Enum):   
    Pending = "Pending"
    InProgress = "In Progress"
    Resolved = "Resolved"


class FeeStatus(str, Enum):
    Paid = "Paid"
    Unpaid = "Unpaid"
    Partial = "Partial"


class OccupancyStatus(str, Enum):
    Vacant = "Vacant"
    Occupied = "Occupied"

class NoticeStatus(str, Enum):
    Active = "Active"
    Inactive = "Inactive"


# ---------------- Complaints ----------------
class ComplaintBase(BaseModel):
    student_name: str
    category: str
    description: str
    status: ComplaintStatus

class ComplaintResponse(ComplaintBase):
    id: int

    class Config:
        from_attributes = True

class ComplaintStatusUpdate(BaseModel):
    
    status: ComplaintStatus

# ---------------- Notices ----------------
class NoticeBase(BaseModel):
    title: str
    description: str
class NoticeUpdate(BaseModel):
    title: str
    description: str
class NoticeResponse(NoticeBase):
    id: int

    class Config:
        from_attributes = True

# ---------------- Fee Collection ----------------
class FeeCollectionBase(BaseModel):
    student_name: str
    student_id: str
    amount: float
    date: str
    status: FeeStatus

class FeeCollectionUpdate(BaseModel):
    amount: float
    status: FeeStatus

class FeeCollectionResponse(FeeCollectionBase):
    id: int

    class Config:
        from_attributes = True

# ---------------- Dashboard ----------------

class DashboardBase(BaseModel):
    occupancy_percent: float
    fee_collection: float
    complaints_count:int
    notice: str
class DashboardResponse(DashboardBase):
    id: int
    total_users: Optional[int]=None
    active_users: Optional[int]=None
    complaints_count: int
    notices_count: Optional[int]=None
    class Config:
        from_attributes = True
#---------------- Occupancy ----------------
class OccupancyBase(BaseModel):
    room_number: str
    status: OccupancyStatus

class OccupancyResponse(OccupancyBase):
    id: int

    class Config:
        from_attributes = True

