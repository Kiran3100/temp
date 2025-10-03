from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.models.admin_dashboard import Dashboard
from app.schemas.admin_dashboard import NoticeBase, NoticeResponse, NoticeUpdate, NoticeStatus
from app.db.session import get_db


router = APIRouter()



# ---------------- Notices CRUD ----------------
@router.post("/notices/", response_model=NoticeResponse, tags=["Admin Notices"])
def add_notice(notice: NoticeBase, db: Session = Depends(get_db)):
    db_notice = Dashboard.Notice(**notice.dict())
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return db_notice

@router.get("/notices/", response_model=list[NoticeResponse], tags=["Admin Notices"])
def get_all_notices(db: Session = Depends(get_db)):
    return db.query(Dashboard.Notice).all()

@router.put("/notices/{notice_id}", response_model=NoticeResponse, tags=["Admin Notices"])
def update_notice(notice_id: int, notice: NoticeUpdate, db: Session = Depends(get_db)):
    db_notice = db.query(Dashboard.Notice).filter(Dashboard.Notice.id == notice_id).first()
    if not db_notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    db_notice.title = notice.title
    db_notice.description = notice.description
    db.commit()
    db.refresh(db_notice)
    return db_notice

@router.delete("/notices/{notice_id}", tags=["Admin Notices"])
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    db_notice = db.query(Dashboard.Notice).filter(Dashboard.Notice.id == notice_id).first()
    if not db_notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    db.delete(db_notice)
    db.commit()
    return {"detail": "Notice deleted"}
