# TODO: Mentor - Import stripe library after installation
# import stripe

from app.core.config import settings


class StripeProvider:
    def __init__(self):
        # TODO:Initialize stripe with API Key from settings
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        pass

    def create_checkout_session(self, order_id: int, amount_cents: int, currency: str):

        # TODO: Implement actual Stripe Checkout Session creation
        # session = stripe.checkout.Session.create(...)

        mock_url = f"https://checkout.stripe.com/pay/mock_{order_id}"
        mock_session_id = f"cs_test_{order_id}"

        return {
            "checkout_url": mock_url,
            "session_id": mock_session_id
        }

    def verify_webhook(self, payload: bytes, sig_header: str):
        # TODO: Implement stripe webhook signature verification
        # event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        # return event
        pass