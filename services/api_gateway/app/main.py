from fastapi import FastAPI, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route
from app.routes.auth import router as auth_router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/")
async def root():
    return {"message": "API Gateway Service API", "version": "0.1.0"}