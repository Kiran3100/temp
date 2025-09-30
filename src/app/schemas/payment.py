
from pydantic import BaseModel
from decimal import Decimal

class InvoiceCreate(BaseModel):
    tenant_id: int
    amount: Decimal
    currency: str = "INR"

class InvoiceOut(BaseModel):
    id: int
    tenant_id: int
    amount: Decimal
    currency: str
    status: str

    class Config:
        orm_mode = True
