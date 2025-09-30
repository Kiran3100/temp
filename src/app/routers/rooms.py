from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select
from app.schemas.room import RoomCreate, RoomOut
from app.models.tenant import Room as RoomModel
from app.db.session import get_tenant_db
from typing import List
from app.dependencies.auth import get_current_tenant_user

router = APIRouter()


async def tenant_db_for_request(request: Request):
    tenant_schema = getattr(request.state, "tenant_schema", None)
    if not tenant_schema:
        raise HTTPException(status_code=400, detail="Tenant header (X-Hostel-ID) required")
    return get_tenant_db(tenant_schema)


@router.post("/", response_model=RoomOut)
async def create_room(payload: RoomCreate, ctx=Depends(get_current_tenant_user)):
    tenant_schema = ctx["tenant_schema"]
    async with get_tenant_db(tenant_schema) as session:
        room = RoomModel(floor_id=payload.floor_id, number=payload.number, capacity=payload.capacity)
        session.add(room)
        await session.commit()
        await session.refresh(room)
        return room


@router.get("/", response_model=List[RoomOut])
async def list_rooms(ctx=Depends(get_current_tenant_user)):
    tenant_schema = ctx["tenant_schema"]
    async with get_tenant_db(tenant_schema) as session:
        q = await session.execute(select(RoomModel).order_by(RoomModel.id))
        return q.scalars().all()