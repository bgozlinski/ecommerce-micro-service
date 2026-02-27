from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class CartAdd(BaseModel):
    """Schema for adding a product to the shopping cart."""
    product_id: int
    quantity: int


class CartPatch(BaseModel):
    """Schema for updating cart item quantity."""
    quantity: int


class CartItemOut(BaseModel):
    """Schema for returning a single item in the cart."""
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderItemOut(BaseModel):
    """Schema for returning a single item within an order."""
    id: int
    product_id: int
    quantity: int
    unit_price_cents: int
    total_price_cents: int

    model_config = ConfigDict(from_attributes=True)


class OrderOut(BaseModel):
    """Schema for returning full order details, including status and items."""
    id: int
    user_id: int
    status: str
    total_amount_cents: int
    currency: str
    created_at: datetime
    paid_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    items: List[OrderItemOut]

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Simple message response (e.g., for cancellation confirmation)."""
    message: str


class KeysResponse(BaseModel):
    """Schema for returning assigned license keys for a paid order."""
    keys: List[str]


class PaymentStatusUpdate(BaseModel):
    """Schema for payment status update request from Payment Service."""
    status: str
    payment_id: Optional[str] = None
