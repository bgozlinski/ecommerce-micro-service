from sqlalchemy.orm import Session
from app.models.payment import Payment
from datetime import datetime, timezone


def create_payment(db: Session, order_id: int, amount_cents: int, currency: str = "PLN") -> Payment:
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
    """Pobiera płatność po ID"""
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_order_id(db: Session, order_id: int) -> Payment:
    """Pobiera płatność po order_id"""
    return db.query(Payment).filter(Payment.order_id == order_id).first()


def get_payment_by_external_id(db: Session, external_payment_id: str) -> Payment:
    """Pobiera płatność po external_payment_id (Stripe session ID)"""
    return db.query(Payment).filter(Payment.external_payment_id == external_payment_id).first()