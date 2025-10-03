from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import tenants_models
from app.schemas import tenants_schemas
from app.db.session import get_db
from sqlalchemy import func

router = APIRouter(prefix="/notices", tags=["Tenants Notices"])

# ---------- Dashboard Update Function ----------
def update_dashboard(db: Session):
    dashboard = db.query(tenants_models.Dashboard).first()
    if not dashboard:
        dashboard = tenants_models.Dashboard()
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)

    dashboard.total_profiles = db.query(tenants_models.Profile).count()
    dashboard.total_payments = db.query(tenants_models.Payment).count()
    dashboard.total_paid_amount = db.query(func.sum(tenants_models.Payment.amount)).scalar() or 0
    dashboard.recent_payments = ",".join(
        str(p.id) for p in db.query(tenants_models.Payment).order_by(tenants_models.Payment.paid_on.desc()).limit(5)
    )
    dashboard.notices_count = db.query(tenants_models.Notice).count()
    db.commit()


# ---------- Create Notice ----------
@router.post("/", response_model=tenants_schemas.Notice)
def create_notice(notice: tenants_schemas.NoticeCreate, db: Session = Depends(get_db)):
    new_notice = tenants_models.Notice(**notice.dict())
    db.add(new_notice)
    db.commit()
    db.refresh(new_notice)
    update_dashboard(db)
    return new_notice


# ---------- Read All Notices ----------
@router.get("/", response_model=list[tenants_schemas.Notice])
def get_notices(db: Session = Depends(get_db)):
    return db.query(tenants_models.Notice).order_by(tenants_models.Notice.created_at.desc()).all()


# ---------- Read Single Notice ----------
@router.get("/{notice_id}", response_model=tenants_schemas.Notice)
def read_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = db.query(tenants_models.Notice).filter(tenants_models.Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice


# ---------- Update Notice ----------
@router.put("/{notice_id}", response_model=tenants_schemas.Notice)
def update_notice(notice_id: int, updated_notice: tenants_schemas.NoticeUpdate, db: Session = Depends(get_db)):
    notice = db.query(tenants_models.Notice).filter(tenants_models.Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    if updated_notice.title is not None:
        notice.title = updated_notice.title
    if updated_notice.description is not None:
        notice.description = updated_notice.description

    db.commit()
    db.refresh(notice)
    update_dashboard(db)
    return notice


# ---------- Delete Notice ----------
@router.delete("/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = db.query(tenants_models.Notice).filter(tenants_models.Notice.id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    db.delete(notice)
    db.commit()
    update_dashboard(db)
    return {"message": "Notice deleted successfully"}
