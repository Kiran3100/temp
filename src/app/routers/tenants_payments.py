from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.models import tenants_models
from app.schemas import tenants_schemas
from app.db.session import get_db

router = APIRouter(prefix="/payments", tags=["Tenants Payments"])

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
        str(p.id) for p in db.query(models.Payment).order_by(tenants_models.Payment.paid_on.desc()).limit(5)
    )
    dashboard.notices_count = db.query(tenants_models.Notice).count()
    db.commit()


# ---------- Create Payment ----------
@router.post("/", response_model=tenants_schemas.Payment)
def create_payment(payment: tenants_schemas.PaymentCreate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(tenants_models.Profile).filter(tenants_models.Profile.id == payment.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User does not exist")

    new_payment = tenants_models.Payment(**payment.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    update_dashboard(db)
    return new_payment


# ---------- Read All Payments ----------
@router.get("/", response_model=list[tenants_schemas.Payment])
def get_payments(db: Session = Depends(get_db)):
    return db.query(tenants_models.Payment).all()


# ---------- Read Single Payment ----------
@router.get("/{payment_id}", response_model=tenants_schemas.Payment)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(tenants_models.Payment).filter(tenants_models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


# ---------- Update Payment ----------
@router.put("/{payment_id}", response_model=tenants_schemas.Payment)
def update_payment(payment_id: int, updated_payment: tenants_schemas.PaymentUpdate, db: Session = Depends(get_db)):
    payment = db.query(tenants_models.Payment).filter(tenants_models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if updated_payment.status:
        payment.status = updated_payment.status
        if updated_payment.status.lower() == "paid":
            payment.paid_on = datetime.utcnow()

    if updated_payment.amount is not None:
        payment.amount = updated_payment.amount

    db.commit()
    db.refresh(payment)
    update_dashboard(db)
    return payment


# ---------- Delete Payment ----------
@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(tenants_models.Payment).filter(tenants_models.Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(payment)
    db.commit()
    update_dashboard(db)
    return {"message": "Payment deleted successfully"}
