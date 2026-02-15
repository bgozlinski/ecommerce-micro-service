"""Order Service FastAPI application.

This service manages shopping carts, order creation, and order lifecycle.
It coordinates with Product Catalog and Inventory services for stock
management and publishes events to Kafka for downstream processing.
"""

from fastapi import FastAPI
from app.routes.order import router as order_router

app = FastAPI()

app.include_router(order_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}

@app.get("/")
async def root():
    return {"message": "Order Service APIi", "version": "0.1.0"}
