from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas.admin_dashboard import DashboardResponse
from app.db.session import get_db
from app.models.admin_dashboard import Complaint,Occupancy,FeeCollection,Notice,Dashboard



router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])



# ---------------- Dashboard ----------------

@router.get("/dashboard", response_model=DashboardResponse, tags=["Admin Dashboard"])
def get_dashboard_data(db: Session = Depends(get_db)):
    # Complaints count
    total_complaints = db.query(func.count(Complaint.id)).scalar()

    # Occupancy %
    total_rooms = db.query(func.count(Occupancy.id)).scalar()
    occupied_rooms = (
        db.query(func.count(Occupancy.id))
        .filter(Occupancy.status == "Occupied")
        .scalar()
    )
    occupancy_percent = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    # Fee collection
    total_fee = (
        db.query(func.sum(FeeCollection.amount))
        .filter(FeeCollection.status == "Paid")
        .scalar()
    ) or 0

    # Latest notice (title + description)
    latest_notice_row = (
        db.query(Notice.title, Notice.description)
        .order_by(Notice.id.desc())
        .first()
    )
    latest_notice = latest_notice_row.title if latest_notice_row else None

    # ✅ Save into Dashboard table
    dashboard_entry = Dashboard(
        occupancy_percent=occupancy_percent,
        fee_collection=total_fee,
        complaints=total_complaints,
        # complaints_count=total_complaints,
        notice=latest_notice,
    )
    db.add(dashboard_entry)
    db.commit()
    db.refresh(dashboard_entry)

    # For Pydantic v2
    return DashboardResponse.model_validate({
    "id": dashboard_entry.id,
    "occupancy_percent": dashboard_entry.occupancy_percent,
    "fee_collection": dashboard_entry.fee_collection,
    "complaints_count": total_complaints,
    "total_users": 0,        # supply actual value if available
    "active_users": 0,       # supply actual value if available
    "notices_count": 0,      # supply actual value if available
    "notice": dashboard_entry.notice,
    })


