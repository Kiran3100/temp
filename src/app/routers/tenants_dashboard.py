from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import tenants_models
from app.schemas import tenants_schemas
from app.db.session import get_db

router = APIRouter(prefix="/tenant", tags=["Tenants Dashboard"])


# ---------- Dashboard Helper Function ----------
def get_dashboard_summary(db: Session) -> dict:
    dashboard = db.query(tenants_models.Dashboard).first()
    if not dashboard:
        # If dashboard doesn't exist, create it
        dashboard = tenants_models.Dashboard()
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)

    # Fetch related data
    total_profiles = db.query(tenants_models.Profile).count()

    # ✅ Count only "paid" payments
    total_payments = db.query(tenants_models.Payment).filter(tenants_models.Payment.status == "Paid").count()

    # ✅ Sum only "paid" payment amounts
    total_paid_amount = (
        db.query(func.sum(tenants_models.Payment.amount))
        .filter(tenants_models.Payment.status == "Paid")
        .scalar()
        or 0
    )

    # ✅ Fetch only recent "paid" payments
    recent_payments_objs = (
        db.query(tenants_models.Payment)
        .filter(tenants_models.Payment.status == "Paid")
        .order_by(tenants_models.Payment.paid_on.desc())
        .limit(5)
        .all()
    )
    recent_payments = [tenants_schemas.Payment.model_validate(p) for p in recent_payments_objs]

    # Notices
    notices_objs = db.query(tenants_models.Notice).order_by(tenants_models.Notice.created_at.desc()).all()
    notices = [tenants_schemas.Notice.model_validate(n) for n in notices_objs]

    # Update dashboard table
    dashboard.total_profiles = total_profiles
    dashboard.total_payments = total_payments
    dashboard.total_paid_amount = total_paid_amount
    dashboard.recent_payments = ",".join(str(p.id) for p in recent_payments_objs)
    dashboard.notices_count = len(notices_objs)

    db.commit()
    db.refresh(dashboard)

    return {
        "total_profiles": total_profiles,
        "total_payments": total_payments,
        "total_paid_amount": total_paid_amount,
        "recent_payments": recent_payments,
        "notices": notices,
    }


# ---------- Get Dashboard ----------
@router.get("/", response_model=tenants_schemas.Dashboard)
def get_dashboard(db: Session = Depends(get_db)):
    return get_dashboard_summary(db)
