from fastapi import FastAPI
from app.routes.payment import router as payment_router

app = FastAPI()

app.include_router(payment_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}

@app.get("/")
async def root():
    return {"message": "Payment Service API", "version": "0.1.0"}
