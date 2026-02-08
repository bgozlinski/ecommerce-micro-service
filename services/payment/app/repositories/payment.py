"""Repository layer for payment database operations.

This module provides data access functions for the Payment model,
abstracting database queries from business logic.
"""

from sqlalchemy.orm import Session
from app.models.payment import Payment
from datetime import datetime, timezone


def create_payment(db: Session, order_id: int, amount_cents: int, currency: str = "PLN") -> Payment:
    """Create a new payment record with pending status.

    Args:
        db: Database session.
        order_id: ID of the associated order.
        amount_cents: Payment amount in cents.
        currency: ISO 4217 currency code. Defaults to "PLN".

    Returns:
        Payment: The newly created payment record.
    """
    payment = Payment(
        order_id=order_id,
        amount_cents=amount_cents,
        currency=currency,
        status="pending",
        provider="Stripe"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def update_payment_status(
        db: Session,
        payment_id: int,
        status: str,
        external_payment_id: str = None
) -> Payment:
    """Update payment status and external reference.

    Args:
        db: Database session.
        payment_id: ID of the payment to update.
        status: New payment status ("pending", "success", "failed").
        external_payment_id: Stripe session/payment ID. Optional.

    Returns:
        Payment: Updated payment record, or None if not found.
    """
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return None

    payment.status = status
    payment.external_payment_id = external_payment_id
    payment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_id(db: Session, payment_id: int) -> Payment:
    """Retrieve a payment by its ID.

    Args:
        db: Database session.
        payment_id: Payment identifier.

    Returns:
        Payment: Payment record, or None if not found.
    """
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_order_id(db: Session, order_id: int) -> Payment:
    """Retrieve a payment by associated order ID.

    Args:
        db: Database session.
        order_id: Order identifier.

    Returns:
        Payment: Payment record, or None if not found.
    """
    return db.query(Payment).filter(Payment.order_id == order_id).first()


def get_payment_by_external_id(db: Session, external_payment_id: str) -> Payment:
    """Retrieve a payment by Stripe session ID.

    Args:
        db: Database session.
        external_payment_id: Stripe checkout session or payment intent ID.

    Returns:
        Payment: Payment record, or None if not found.
    """
    return db.query(Payment).filter(Payment.external_payment_id == external_payment_id).first()