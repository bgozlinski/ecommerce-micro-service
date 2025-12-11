from fastapi import FastAPI
from app.routes.product import router as product_router

app = FastAPI()

app.include_router(product_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service"}

@app.get("/")
async def root():
    return {"message": "Product Service API", "version": "0.1.0"}
