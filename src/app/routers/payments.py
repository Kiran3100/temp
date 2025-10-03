from fastapi import APIRouter, Request, Header, HTTPException, Depends
from app.core.config import settings
import hmac, hashlib
from sqlalchemy import select
from app.schemas.payment import InvoiceCreate, InvoiceOut
from app.models.tenant import Invoice as InvoiceModel
from app.db.session import get_db
from decimal import Decimal
from typing import List
from app.dependencies.auth import get_current_tenant_user
from app.utils.tenant_utils import filter_tenant_records, tenant_scoped_filter_query
from app.models.tenant import Invoice as InvoiceModel  

router = APIRouter()

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")
    # In real code use stripe library to construct event with webhook secret
    # Placeholder: verify signature, process payment intent succeeded events.
    return {"ok": True}

@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, x_razorpay_signature: str = Header(None)):
    payload = await request.body()
    # verify with RAZORPAY_WEBHOOK_SECRET
    return {"ok": True}

async def tenant_db_for_request(request: Request):
    tenant_schema = getattr(request.state, "tenant_schema", None)
    if not tenant_schema:
        raise HTTPException(status_code=400, detail="Tenant header (X-Hostel-ID) required")
    return get_db(tenant_schema)


    
    
@router.post("/invoices", response_model=InvoiceOut)
async def create_invoice(payload: InvoiceCreate, ctx=Depends(get_current_tenant_user)):
    tenant_schema = ctx["tenant_schema"]
    async with get_db(tenant_schema) as session:
        inv = InvoiceModel(
            tenant_id=payload.tenant_id,
            amount=payload.amount,
            currency=payload.currency,
            status="pending",
        )
        session.add(inv)
        await session.commit()
        await session.refresh(inv)
        return inv

    
@router.get("/invoices", response_model=List[InvoiceOut])
async def list_invoices(ctx=Depends(get_current_tenant_user)):
    tenant_schema = ctx["tenant_schema"]
    user = ctx["user"]

    async with get_db(tenant_schema) as session:
        q = select(InvoiceModel).order_by(InvoiceModel.id)  # Use InvoiceModel
        q = tenant_scoped_filter_query(user, q, InvoiceModel)
        rows = (await session.execute(q)).scalars().all()
        return rows

@router.post("/webhook/{provider}")
async def payment_webhook(provider: str, request: Request):
    """
    Webhook stub for payment providers (stripe / razorpay etc.)
    You must verify signature and update invoice status accordingly.
    """
    body = await request.body()
    headers = dict(request.headers)
    # Placeholder: parse and verify according to provider; update invoice in tenant DB as needed.
    return {"ok": True, "provider": provider, "received": len(body)}
