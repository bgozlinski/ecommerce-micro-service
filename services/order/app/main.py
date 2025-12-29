from fastapi import FastAPI
from app.routes.order import router as order_router

app = FastAPI()

app.include_router(order_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}

@app.get("/")
async def root():
    return {"message": "Order Service API", "version": "0.1.0"}
