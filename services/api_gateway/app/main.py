"""FastAPI application entry-point for the API Gateway.

The gateway routes external HTTP requests to internal microservices. Routers are
mounted under a shared API prefix (e.g., `/api/v1`). Health and root endpoints
are provided for basic diagnostics and metadata.
"""

from fastapi import FastAPI, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route
from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.product import router as product_router
from app.routes.order import router as order_router
from app.routes.inventory import router as inventory_router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(users_router, prefix=settings.API_V1_PREFIX, tags=["users"])
app.include_router(product_router, prefix=settings.API_V1_PREFIX, tags=["product-catalog"])
app.include_router(inventory_router, prefix=settings.API_V1_PREFIX, tags=["inventory"])
app.include_router(order_router, prefix=settings.API_V1_PREFIX, tags=["orders"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/")
async def root():
    return {"message": "API Gateway Service API", "version": "0.1.0"}