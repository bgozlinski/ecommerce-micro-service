"""Pydantic schemas for payment request/response validation.

This module defines data transfer objects (DTOs) for payment-related
API endpoints, ensuring type safety and validation.
"""

from pydantic import BaseModel
from typing import Optional

class PaymentCreate(BaseModel):
    """Request schema for creating a new payment.

    Attributes:
        order_id: ID of the order to be paid.
        amount_cents: Payment amount in cents.
        currency: ISO 4217 currency code. Defaults to "PLN".
    """

    order_id: int
    amount_cents: int
    currency: str = "PLN"

class PaymentResponse(BaseModel):
    """Response schema after creating a payment.

    Attributes:
        payment_id: ID of the created payment record.
        checkout_url: Stripe Checkout session URL for user payment.
        status: Current payment status (typically "pending" on creation).
    """

    payment_id: int
    checkout_url: str
    status: str