"""Authentication API endpoints.

This module defines REST API routes for user authentication, including
login with JWT token generation.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.auth import authenticate_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and generate access token.
    
    Validates user credentials (email and password) and returns a JWT access
    token upon successful authentication. The token can be used for subsequent
    authenticated requests.
    
    Args:
        payload: Login credentials (email and password).
        db: Database session dependency.
        
    Returns:
        TokenResponse: Contains access_token, token_type, and expires_in.
        
    Raises:
        HTTPException: 401 if credentials are incorrect.
        HTTPException: 403 if user account is inactive.
    """
    token, expires_in = authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in
    )
