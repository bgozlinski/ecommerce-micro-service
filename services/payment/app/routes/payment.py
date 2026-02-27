"""Payment API endpoints.

This module defines REST API routes for payment processing, including
Stripe Checkout session creation, webhook handling, and payment status queries.
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.repositories import payment as payment_repo
from app.schemas.payment import PaymentCreate, PaymentResponse
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
    """Create a Stripe Checkout session for an order.

    This endpoint verifies the order exists and has "awaiting_payment" status,
    creates a payment record in the database, and generates a Stripe Checkout
    session URL for the user to complete payment.

    Workflow:
        1. Verify order exists and status is "awaiting_payment"
        2. Check no payment already exists for this order
        3. Create payment record (status: pending)
        4. Create Stripe Checkout session
        5. Update payment with Stripe session ID
        6. Return checkout URL

    Args:
        payload: Payment creation request containing order_id, amount, currency.
        db: Database session dependency.

    Returns:
        PaymentResponse: Contains payment_id, checkout_url, and status.

    Raises:
        HTTPException: 404 if order not found.
        HTTPException: 400 if order status is not "awaiting_payment" or payment exists.
        HTTPException: 503 if Order Service is unavailable.
        HTTPException: 500 if Stripe session creation fails.
    """
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
    if existing_payment and existing_payment.status == "success":
        raise HTTPException(
            status_code=400,
            detail="Order is already paid"
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
    """Handle Stripe webhook events.

    This endpoint receives and processes webhook events from Stripe, verifying
    the signature and handling payment completion or expiration. On successful
    payment, it notifies the Order Service to update order status and confirm
    inventory reservations.

    Supported events:
        - checkout.session.completed: Payment successful
        - checkout.session.expired: Payment session expired without completion

    Args:
        request: FastAPI request object containing webhook payload and signature.
        db: Database session dependency.

    Returns:
        dict: Status message indicating event processing result.

    Raises:
        HTTPException: 400 if payload or signature is invalid.

    Notes:
        - This endpoint does NOT require authentication (called by Stripe).
        - Signature verification ensures request authenticity.
        - Order Service is notified via REST API (not through API Gateway).
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    logger.info(f"Incoming Stripe Webhook request. Signature: {sig_header[:10] if sig_header else 'None'}...")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload in webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature in webhook. Check your STRIPE_WEBHOOK_SECRET settings. Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    logger.info(f"Received Stripe event: {event['type']}")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        order_id = session["metadata"].get("order_id")
        payment_id = session["metadata"].get("payment_id")

        logger.info(f"Checkout session completed. Metadata: order_id={order_id}, payment_id={payment_id}")

        if not order_id or not payment_id:
            logger.error(f"Missing order_id or payment_id in metadata. Session ID: {session['id']}")
            return {"status": "error", "message": "Missing metadata"}

        logger.info(f"Attempting to update payment {payment_id} to success")
        payment = payment_repo.update_payment_status(
            db=db,
            payment_id=int(payment_id),
            status="success",
            external_payment_id=session["id"]
        )

        if not payment:
            logger.error(f"Payment record with ID {payment_id} not found in database")
            return {"status": "error", "message": "Payment not found"}

        logger.info(f"Payment {payment_id} updated to success. External ID: {session['id']}")

        try:
            logger.info(f"Notifying Order Service for order {order_id} with status success")
            response = requests.post(
                f"{settings.ORDER_SERVICE_URL}/api/v1/orders/{order_id}/payment-status",
                json={
                    "status": "success",
                    "payment_id": session["id"]
                },
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"Order {order_id} marked as paid successfully")
            else:
                logger.error(f"Failed to update order status for {order_id}. Status code: {response.status_code}, Response: {response.text}")

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


@router.post("/verify/{order_id}")
async def verify_payment(order_id: int, db: Session = Depends(get_db)):
    """Verify payment status by checking Stripe session directly.

    This endpoint is called by the frontend after returning from Stripe Checkout.
    It retrieves the Stripe session using the stored external_payment_id and checks
    if the payment was completed. If so, it updates the payment and order status.

    This serves as a fallback when Stripe webhooks cannot reach localhost.

    Args:
        order_id: Order identifier.
        db: Database session dependency.

    Returns:
        dict: Verification result with payment and order status.

    Raises:
        HTTPException: 404 if no payment found for the order.
    """
    payment = payment_repo.get_payment_by_order_id(db, order_id)
    if not payment:
        raise HTTPException(status_code=404, detail="No payment found for this order")

    if payment.status == "success":
        return {"status": "already_paid", "payment_status": "success"}

    if not payment.external_payment_id:
        return {"status": "no_session", "payment_status": payment.status}

    try:
        session = stripe.checkout.Session.retrieve(payment.external_payment_id)
        logger.info(f"Stripe session {payment.external_payment_id} status: {session.payment_status}")

        if session.payment_status == "paid":
            payment_repo.update_payment_status(
                db=db,
                payment_id=payment.id,
                status="success",
                external_payment_id=session.id
            )

            try:
                response = requests.post(
                    f"{settings.ORDER_SERVICE_URL}/api/v1/orders/{order_id}/payment-status",
                    json={
                        "status": "success",
                        "payment_id": session.id
                    },
                    timeout=10
                )
                logger.info(f"Order {order_id} update response: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to notify Order Service: {e}")

            return {"status": "success", "payment_status": "paid"}

        return {"status": "pending", "payment_status": session.payment_status}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error verifying session: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/{payment_id}")
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Retrieve payment details by ID.

    Args:
        payment_id: Payment identifier.
        db: Database session dependency.

    Returns:
        dict: Payment details including status, amount, and Stripe reference.

    Raises:
        HTTPException: 404 if payment not found.
    """
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