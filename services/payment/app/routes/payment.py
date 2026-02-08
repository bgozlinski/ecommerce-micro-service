import os

from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.database import get_db
from app.core.config import settings
import json
import stripe

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/payments", tags=["payments"])
stripe.api_key = settings.STRIPE_SECRET_KEY

@router.get("/checkout")
async def create_checkout_session(price: int):
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "FastAPI Stripe Checkout",
                    },
                    "unit_amount": price * 100,
                },
                "quantity": 1,
            }
        ],
        metadata={
            "user_id": 3,
            "email": "abc@gmail.com",
            "request_id": 1234567890
        },
        mode="payment",
        success_url='http://localhost:8000/success',
        cancel_url='http://localhost:8000/cancel',
        customer_email="ping@fastapitutorial.com",
    )
    return {"message": "success", "session_url": checkout_session.url}

    return responses.RedirectResponse(checkout_session.url, status_code=303)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    event = None

    try:
        sig_header = request.headers.get("stripe-signature")
        # event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        print("Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature")
        raise HTTPException(status_code=400, detail="Invalid signature")

    print("event received is", event)
    if event["type"] == "checkout.session.completed":
        payment = event["data"]["object"]
        amount = payment["amount_total"]
        currency = payment["currency"]
        user_id = payment["metadata"]["user_id"]  # get custom user id from metadata
        user_email = payment["customer_details"]["email"]
        user_name = payment["customer_details"]["name"]
        order_id = payment["id"]
        # save to db
        # send email in background task
    return {}