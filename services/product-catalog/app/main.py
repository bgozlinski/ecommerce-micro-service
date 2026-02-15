"""Product Catalog Service FastAPI application.

This service manages the product catalog, including CRUD operations for game
keys and licenses. It handles product filtering, sorting, and status management.
"""

from fastapi import FastAPI
from app.routes.product import router as product_router

app = FastAPI()

app.include_router(product_router)

@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        dict: Service health status.
    """
    return {"status": "healthy", "service": "product-catalog-service"}

@app.get("/")
async def root():
    """Root endpoint providing service metadata.
    
    Returns:
        dict: Service name and version.
    """
    return {"message": "Product Service APIi", "version": "0.1.0"}
