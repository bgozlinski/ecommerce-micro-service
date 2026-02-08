"""Repository layer for authentication operations.

This module provides authentication-related database operations, including
user credential verification and JWT token generation for login.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user import get_user_by_email
from app.core.security import verify_password, create_access_token
from app.core.config import settings

def authenticate_user(db: Session, email: str, password: str) -> tuple[str, int]:
    """Authenticate a user and generate an access token.
    
    Verifies user credentials (email and password), checks if the account is active,
    and generates a JWT access token upon successful authentication.
    
    Args:
        db: Database session.
        email: User's email address.
        password: Plain text password to verify.
        
    Returns:
        tuple[str, int]: A tuple containing:
            - JWT access token (str)
            - Token expiration time in seconds (int)
            
    Raises:
        HTTPException: 401 if credentials are incorrect.
        HTTPException: 403 if user account is inactive.
    """
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })

    expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return token, expiration
