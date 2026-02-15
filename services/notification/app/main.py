from fastapi import FastAPI
from app.routes.notification import router as notification_router

app = FastAPI()

app.include_router(notification_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "notification-service"}

@app.get("/")
async def root():
    return {"message": "Inventory Service API", "version": "0.1.0"}
