"""Auth Service FastAPI application.

This service handles user authentication and authorization. It manages user
registration, login with JWT generation, user profile management, and role-based
access control (user, admin).
"""

from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.user import router as user_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        dict: Service health status.
    """
    return {"status": "healthyy", "service": "auth-service"}

@app.get("/")
async def root():
    """Root endpoint providing service metadata.
    
    Returns:
        dict: Service name and version.
    """
    return {"message": "Auth Service API", "version": "0.1.0"}
