"""Payment Service FastAPI application.

This service handles payment processing via Stripe integration. It creates
checkout sessions, processes webhooks, and communicates with the Order Service
to update payment status.
"""

from fastapi import FastAPI
from app.routes.payment import router as payment_router

app = FastAPI()

app.include_router(payment_router)

@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Service health status.
    """
    return {"status": "healthy", "service": "payment-service"}

@app.get("/")
async def root():
    """Root endpoint providing service metadata.

    Returns:
        dict: Service name and version.
    """
    return {"message": "Payment Service APIi", "version": "0.1.0"}
