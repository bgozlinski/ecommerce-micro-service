from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "inventory-service"}

@app.get("/")
async def root():
    return {"message": "Inventory Service API", "version": "0.1.0"}
