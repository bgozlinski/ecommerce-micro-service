"""Security utilities for password hashing and JWT token generation.

This module provides functions for secure password hashing using bcrypt and
JWT token creation for authentication. It uses passlib for password hashing
and PyJWT for token encoding.
"""

from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta, timezone
import jwt

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash.
        
    Returns:
        str: Hashed password string.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify.
        hashed_password: Hashed password to compare against.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """Create a JWT access token.
    
    Generates a JWT token with the provided data payload and expiration time.
    The token includes 'iat' (issued at) and 'exp' (expiration) claims.
    
    Args:
        data: Dictionary of claims to include in the token payload.
        expires_delta: Token lifetime in minutes. If None, uses default from settings.
        
    Returns:
        str: Encoded JWT token.
        
    Example:
        token = create_access_token(
            data={"sub": user.id, "role": user.role},
            expires_delta=60
        )
    """
    now = datetime.now(timezone.utc)
    minutes = expires_delta if expires_delta is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = now + timedelta(minutes=minutes)

    to_encode = {**data, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}

    encoded_jwt  = jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt
