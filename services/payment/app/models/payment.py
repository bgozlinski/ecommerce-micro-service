"""SQLAlchemy models for payment-related database tables.

This module defines the Payment model representing payment transactions
in the system, including Stripe integration details.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database import Base

class Payment(Base):
    """Payment transaction record.

    Represents a payment transaction processed through Stripe. Tracks the
    payment lifecycle from creation (pending) through completion (success/failed).

    Attributes:
        id: Primary key, auto-incrementing payment identifier.
        order_id: Foreign key reference to the associated order.
        amount_cents: Payment amount in cents (smallest currency unit).
        currency: ISO 4217 currency code (e.g., "PLN", "USD"). Defaults to "PLN".
        status: Payment status. One of: "pending", "success", "failed".
        provider: Payment provider name. Defaults to "Stripe".
        external_payment_id: Stripe session/payment ID for external reference.
        created_at: Timestamp when the payment record was created.
        updated_at: Timestamp of the last update to this record.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, nullable=False, index=True)
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="PLN")
    status = Column(String, nullable=False, default="pending") # pending, success, failed
    provider = Column(String, default="Stripe")
    external_payment_id = Column(String, nullable=True) # ID of Stripe payment
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())