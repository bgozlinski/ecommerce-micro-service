from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.payment import Payment
from app.core.stripe_provider import StripeProvider
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
stripe_provider = StripeProvider()


@router.post("/create", response_model=PaymentResponse)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    db_payment = Payment(
        order_id=payload.order_id,
        amount_cents=payload.amount_cents,
        currency=payload.currency,
        status="pending"
    )
    db.add(db_payment)
    db.flush()

    # TODO: Mentor uzupełni StripeProvider
    stripe_session = stripe_provider.create_checkout_session(
        order_id=payload.order_id,
        amount_cents=payload.amount_cents,
        currency=payload.currency
    )

    db_payment.external_payment_id = stripe_session["session_id"]
    db.commit()

    return {
        "payment_id": db_payment.id,
        "checkout_url": stripe_session["checkout_url"],
        "status": db_payment.status
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint dla Stripe do powiadamiania o statusie płatności.
    """
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    # TODO: Implement webhook processing logic
    # 1. Verify webhook signature
    # 2. If event == "checkout.session.completed" -> Update Payment status to "success"
    # 3. Notify Order Service about successful payment (via REST or Event)

    return {"status": "received"}