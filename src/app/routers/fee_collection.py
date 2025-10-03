

from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from app.models.admin_dashboard import Dashboard
from app.schemas.admin_dashboard import FeeCollectionBase, FeeCollectionUpdate, FeeCollectionResponse


from app.db.session import get_db

router = APIRouter()


# ---------------- Fee Collection CRUD ----------------
@router.post("/Fee Collection", response_model=FeeCollectionResponse, tags=["Fee Collection"])
def add_fee_collection(fee: FeeCollectionBase, db: Session = Depends(get_db)):
    db_fee = Dashboard.FeeCollection(**fee.dict())
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return db_fee

@router.get("/Fee Collection", response_model=list[FeeCollectionResponse], tags=["Fee Collection"])
def get_all_fee_collections(db: Session = Depends(get_db)):
    return db.query(Dashboard.FeeCollection).all()

@router.put("/Fee Collection/{fee_id}", response_model=FeeCollectionResponse, tags=["Fee Collection"])
def update_fee_status(fee_id: int, status: FeeCollectionUpdate, db: Session = Depends(get_db)):
    db_fee = db.query(Dashboard.FeeCollection).filter(Dashboard.FeeCollection.id == fee_id).first()
    if not db_fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    db_fee.status = status.status
    db_fee.amount = status.amount
    db.commit()
    db.refresh(db_fee)
    return db_fee

@router.delete("/Fee Collection/{fee_id}", tags=["Fee Collection"])
def delete_fee_collection(fee_id: int, db: Session = Depends(get_db)):
    db_fee = db.query(Dashboard.FeeCollection).filter(Dashboard.FeeCollection.id == fee_id).first()
    if not db_fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    db.delete(db_fee)
    db.commit()
    return {"detail": "Fee collection record deleted"}