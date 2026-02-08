"""Pydantic schemas for authentication request/response validation.

This module defines data transfer objects (DTOs) for authentication-related
API endpoints, ensuring type safety and validation.
"""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Request schema for user login.
    
    Attributes:
        email: User's email address (validated format).
        password: Plain text password for authentication.
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response schema after successful authentication.
    
    Attributes:
        access_token: JWT access token for authenticated requests.
        token_type: Token type identifier. Defaults to "bearer".
        expires_in: Token lifetime in seconds.
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
