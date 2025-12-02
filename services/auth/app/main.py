from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

@app.get("/")
async def root():
    return {"message": "Auth Service API", "version": "0.1.0"}
