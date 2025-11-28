from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

@app.get("/")
async def root():
    return {"message": "Auth Service API", "version": "0.1.0"}