from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.core.config import settings
from app.core.jwt_middleware import JWTAuthMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(JWTAuthMiddleware, public_paths=settings.PUBLIC_PATHS)
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/")
async def root():
    return {"message": "API Gateway Service API", "version": "0.1.0"}

