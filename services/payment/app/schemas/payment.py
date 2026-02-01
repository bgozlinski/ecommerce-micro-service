from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    order_id: int
    amount_cents: int
    currency: str = "PLN"

class PaymentResponse(BaseModel):
    payment_id: int
    checkout_url: str
    status: str