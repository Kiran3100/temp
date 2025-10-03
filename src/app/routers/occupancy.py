
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.admin_dashboard import Dashboard
from app.schemas.admin_dashboard import OccupancyBase, OccupancyResponse
from app.db.session import get_db


router = APIRouter()

# ---------------- Occupancy CRUD ----------------
@router.post("/Occupancy", response_model=OccupancyResponse, tags=["Occupancy"])
def add_occupancy(record: OccupancyBase, db: Session = Depends(get_db)):
    db_record = Dashboard.Occupancy(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/Occupancy", response_model=list[OccupancyResponse], tags=["Occupancy"])
def get_all_occupancy(db: Session = Depends(get_db)):
    return db.query(Dashboard.Occupancy).all()
