from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from app.db.session import get_db
# from app.services.hostel_service import HostelService
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.schemas.hostel import HostelCreate, HostelOut
from app.schemas.user import Role
from app.db.session import  provision_tenant_schema
from app.models.public import PublicHostel
from typing import List
from decimal import Decimal
from app.dependencies.auth import require_roles  # Use only this import

router = APIRouter()

class HostelCreateIn(BaseModel):
    name: str
    address: str | None = None

@router.post("/", response_model=HostelOut, dependencies=[Depends(require_roles(Role.super_admin.value))])
def create_hostel(payload: HostelCreate, db=Depends(get_db)):
    new = PublicHostel(name=payload.name, address=payload.address)
    db.add(new)
    try:
        db.commit()
        db.refresh(new)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Hostel creation failed")
    tenant_schema = f"hostel_{new.id}"
    provision_tenant_schema(tenant_schema)
    return new


@router.get("/", response_model=List[HostelOut])
def list_hostels(db=Depends(get_db)):
    return db.query(PublicHostel).order_by(PublicHostel.id).all()
