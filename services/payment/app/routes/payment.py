import os
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.repositories import payment as payment_repo
from app.schemas.payment import PaymentCreate, PaymentResponse
import json
import stripe
import requests
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/payments", tags=["payments"])
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
        payload: PaymentCreate,
        db: Session = Depends(get_db)
):

    try:
        order_response = requests.get(
            f"{settings.ORDER_SERVICE_URL}/api/v1/orders/internal/{payload.order_id}",
            timeout=5
        )
        if order_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Order not found")

        order_data = order_response.json()
        if order_data["status"] != "awaiting_payment":
            raise HTTPException(
                status_code=400,
                detail=f"Order status must be 'awaiting_payment', current: {order_data['status']}"
            )
    except requests.RequestException as e:
        logger.error(f"Failed to fetch order: {e}")
        raise HTTPException(status_code=503, detail="Order service unavailable")

    existing_payment = payment_repo.get_payment_by_order_id(db, payload.order_id)
    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment for this order already exists"
        )

    payment = payment_repo.create_payment(
        db=db,
        order_id=payload.order_id,
        amount_cents=payload.amount_cents,
        currency=payload.currency
    )

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": payload.currency.lower(),
                        "product_data": {
                            "name": f"Order #{payload.order_id}",
                        },
                        "unit_amount": payload.amount_cents,
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "order_id": payload.order_id,
                "payment_id": payment.id,
            },
            mode="payment",
            success_url=f'{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.FRONTEND_URL}/payment/cancel?order_id={payload.order_id}',
        )

        # 5. Zapisz Stripe session ID jako external_payment_id
        payment_repo.update_payment_status(
            db=db,
            payment_id=payment.id,
            status="pending",
            external_payment_id=checkout_session.id
        )

        return PaymentResponse(
            payment_id=payment.id,
            checkout_url=checkout_session.url,
            status="pending"
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Stripe checkout session")


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info(f"Received Stripe event: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        order_id = session["metadata"].get("order_id")
        payment_id = session["metadata"].get("payment_id")

        if not order_id or not payment_id:
            logger.error("Missing order_id or payment_id in metadata")
            return {"status": "error", "message": "Missing metadata"}

        payment = payment_repo.update_payment_status(
            db=db,
            payment_id=int(payment_id),
            status="success",
            external_payment_id=session["id"]
        )

        if not payment:
            logger.error(f"Payment {payment_id} not found")
            return {"status": "error", "message": "Payment not found"}

        try:
            response = requests.post(
                f"{settings.ORDER_SERVICE_URL}/api/v1/orders/{order_id}/payment-status",
                json={
                    "status": "success",
                    "payment_id": session["id"]
                },
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Order {order_id} marked as paid")
            else:
                logger.error(f"Failed to update order status: {response.text}")

        except requests.RequestException as e:
            logger.error(f"Failed to notify Order Service: {e}")

        return {"status": "success"}

    elif event["type"] == "checkout.session.expired":
        session = event["data"]["object"]

        order_id = session["metadata"].get("order_id")
        payment_id = session["metadata"].get("payment_id")

        if order_id and payment_id:
            payment_repo.update_payment_status(
                db=db,
                payment_id=int(payment_id),
                status="failed",
                external_payment_id=session["id"]
            )

            try:
                requests.post(
                    f"{settings.ORDER_SERVICE_URL}/api/v1/orders/{order_id}/payment-status",
                    json={"status": "failed"},
                    timeout=10
                )
            except requests.RequestException as e:
                logger.error(f"Failed to notify Order Service: {e}")

        return {"status": "expired"}

    return {"status": "ignored"}


@router.get("/{payment_id}")
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = payment_repo.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount_cents": payment.amount_cents,
        "currency": payment.currency,
        "status": payment.status,
        "provider": payment.provider,
        "external_payment_id": payment.external_payment_id,
        "created_at": payment.created_at,
        "updated_at": payment.updated_at
    }