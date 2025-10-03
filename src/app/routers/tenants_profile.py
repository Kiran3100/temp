from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import tenants_models
from app.schemas import tenants_schemas
from app.db.session import get_db
from sqlalchemy import func

router = APIRouter(prefix="/profiles", tags=["Tenants Profiles"])

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


# ---------- Create or Update Profile ----------
@router.post("/", response_model=tenants_schemas.Profile)
def create_or_update_profile(profile: tenants_schemas.ProfileCreate, db: Session = Depends(get_db)):
    existing_profile = db.query(tenants_models.Profile).filter(tenants_models.Profile.email == profile.email).first()
    
    if existing_profile:
        existing_profile.name = profile.name
        existing_profile.room = profile.room
        db.commit()
        db.refresh(existing_profile)
        update_dashboard(db)
        return existing_profile

    new_profile = tenants_models.Profile(**profile.dict())
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    update_dashboard(db)
    return new_profile


# ---------- Read All Profiles ----------
@router.get("/", response_model=list[tenants_schemas.Profile])
def get_profiles(db: Session = Depends(get_db)):
    return db.query(tenants_models.Profile).all()


# ---------- Read Single Profile ----------
@router.get("/{profile_id}", response_model=tenants_schemas.Profile)
def read_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(tenants_models.Profile).filter(tenants_models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


# ---------- Delete Profile ----------
@router.delete("/{profile_id}")
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.query(tenants_models.Profile).filter(tenants_models.Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(profile)
    db.commit()
    update_dashboard(db)
    return {"message": "Profile deleted successfully"}
