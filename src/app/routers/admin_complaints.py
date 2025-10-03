from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.models.admin_dashboard import Dashboard
from app.schemas.admin_dashboard import ComplaintStatusUpdate,ComplaintResponse,ComplaintBase

from app.db.session import get_db
router = APIRouter(prefix="/admin", tags=["Admin Complaints"])


# ---------------- Complaints CRUD ----------------
@router.post("/complaints/", response_model=ComplaintResponse, )
def add_complaint(complaint: ComplaintBase, db: Session = Depends(get_db)):
    db_complaint = Dashboard.Complaint(**complaint.dict())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

@router.get("/complaints/", response_model=list[ComplaintResponse])
def get_all_complaints(db: Session = Depends(get_db)):
    return db.query(Dashboard.Complaint).all()

@router.put("/complaints/{complaint_id}", response_model=ComplaintResponse)
def update_complaint_status(complaint_id: int, status:ComplaintStatusUpdate, db: Session = Depends(get_db)):
    db_complaint = db.query(Dashboard.Complaint).filter(Dashboard.Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db_complaint.status = status.status
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

@router.delete("/complaints/{complaint_id}")
def delete_complaint(complaint_id: int, db: Session = Depends(get_db)):
    db_complaint = db.query(Dashboard.Complaint).filter(Dashboard.Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db.delete(db_complaint)
    db.commit()
    return {"detail": "Complaint deleted"}
