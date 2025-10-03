# src/app/routers/beds.py
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select, update
from app.schemas.bed import BedCreate, BedOut, BedAssign
from app.models.tenant import Bed as BedModel
from app.db.session import get_db
from typing import List
from app.dependencies.auth import get_current_tenant_user
from app.utils.tenant_utils import filter_tenant_records

router = APIRouter()


async def tenant_db_for_request(request: Request):
    tenant_schema = getattr(request.state, "tenant_schema", None)
    if not tenant_schema:
        raise HTTPException(status_code=400, detail="Tenant header (X-Hostel-ID) required")
    return get_db(tenant_schema)


@router.post("/", response_model=BedOut)
async def create_bed(payload: BedCreate, ctx=Depends(get_current_tenant_user)):
    tenant_schema = ctx["tenant_schema"]
    async with get_db(tenant_schema) as session:
        bed = BedModel(room_id=payload.room_id, bed_no=payload.bed_no)
        session.add(bed)
        await session.commit()
        await session.refresh(bed)
        return bed
    
@router.get("/", response_model=List[BedOut])
async def list_beds(ctx=Depends(get_current_tenant_user)):
    tenant_schema = ctx["tenant_schema"]
    user = ctx["user"]

    async with get_db(tenant_schema) as session:
        q = await session.execute(select(BedModel).order_by(BedModel.id))
        beds = q.scalars().all()

        # If tenant role: filter only their bed
        if "tenant" in user["roles"]:
            beds = [b for b in beds if b.tenant_id == user["id"]]

        return beds


@router.post("/{bed_id}/assign", response_model=BedOut)
async def assign_bed(bed_id: int, payload: BedAssign, request: Request, db_dep=Depends(tenant_db_for_request)):
    async with (await db_dep) as session:
        q = await session.execute(select(BedModel).where(BedModel.id == bed_id))
        bed = q.scalars().first()
        if not bed:
            raise HTTPException(status_code=404, detail="Bed not found")
        if bed.occupied:
            raise HTTPException(status_code=400, detail="Bed already occupied")
        # assign
        bed.tenant_id = payload.tenant_id
        bed.occupied = True
        session.add(bed)
        await session.commit()
        await session.refresh(bed)
        return bed
