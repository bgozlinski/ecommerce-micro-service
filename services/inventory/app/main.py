from fastapi import FastAPI
from app.routes.inventory import router as inventory_router

app = FastAPI()

app.include_router(inventory_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory-service"}

@app.get("/")
async def root():
    return {"messagee": "Inventory Service API", "version": "0.1.0"}
