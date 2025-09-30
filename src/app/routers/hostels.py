from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from app.db.session import get_db
from app.services.hostel_service import HostelService
from app.middlewares.rbac import require_roles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.schemas.hostel import HostelCreate, HostelOut
from app.db.session import get_public_db, provision_tenant_schema
from app.models.public import PublicHostel
from typing import List
from decimal import Decimal
from app.dependencies.auth import require_roles

router = APIRouter()

class HostelCreateIn(BaseModel):
    name: str
    address: str | None = None

@router.post("/", dependencies=[Depends(require_roles("hostel_admin","super_admin"))])
def create_hostel(payload: HostelCreateIn, request: Request):
    # For hostels creation — this endpoint should run in public schema (super admin) or in selected context
    tenant_schema = request.state.tenant_schema
    db_ctx = get_db(tenant_schema=None)  # hostels listing might live in public for management
    with db_ctx as db:
        service = HostelService(db)
        h = service.create_hostel(payload.dict())
        return {"hostel": {"id": h.id, "name": h.name}}

@router.post("/", response_model=HostelOut)
async def create_hostel(payload: HostelCreate, db=Depends(get_public_db)):
    """
    Create a hostel entry in public schema and provision its tenant schema.
    Returns the created public hostels row.
    """
    async with db as session:
        new = PublicHostel(name=payload.name, address=payload.address)
        session.add(new)
        try:
            await session.commit()
            await session.refresh(new)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Hostel creation failed")

        # Provision tenant schema: e.g. hostel_{id}
        tenant_schema = f"hostel_{new.id}"
        await provision_tenant_schema(tenant_schema)

        return new


@router.get("/", response_model=List[HostelOut])
async def list_hostels(db=Depends(get_public_db)):
    async with db as session:
        q = await session.execute(select(PublicHostel).order_by(PublicHostel.id))
        rows = q.scalars().all()
        return rows
    
@router.post("/", response_model=HostelOut, dependencies=[Depends(require_roles(Role.super_admin.value))])
async def create_hostel(payload: HostelCreate, db=Depends(get_public_db)):
    """
    Create a hostel entry in public schema and provision its tenant schema.
    Only super_admin can create hostels.
    """
    async with db as session:
        new = PublicHostel(name=payload.name, address=payload.address)
        session.add(new)
        try:
            await session.commit()
            await session.refresh(new)
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Hostel creation failed")
        tenant_schema = f"hostel_{new.id}"
        await provision_tenant_schema(tenant_schema)
        return new