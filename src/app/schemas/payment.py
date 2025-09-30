from pydantic import BaseModel, ConfigDict
from decimal import Decimal

class InvoiceCreate(BaseModel):
    tenant_id: int
    amount: Decimal
    currency: str = "INR"

class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    tenant_id: int
    amount: Decimal
    currency: str
    status: str