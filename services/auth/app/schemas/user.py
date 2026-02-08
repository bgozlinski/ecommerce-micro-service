"""Pydantic schemas for user request/response validation.

This module defines data transfer objects (DTOs) for user-related
API endpoints, ensuring type safety and validation.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields.
    
    Attributes:
        email: User's email address (validated format).
    """
    email: EmailStr


class UserCreate(BaseModel):
    """Request schema for user registration.
    
    Attributes:
        email: User's email address (validated format).
        password: Plain text password (min 8 characters).
    """
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Response schema for user data.
    
    Attributes:
        id: User identifier.
        email: User's email address.
        role: User role ("user" or "admin").
        is_active: Account active status.
        created_at: Account creation timestamp.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime


class UserCreateResponse(BaseModel):
    """Response schema after user creation.
    
    Attributes:
        user: Created user details.
        detail: Success message.
    """
    user: UserResponse
    detail: str = "User created successfully"


class UserDeleteResponse(BaseModel):
    """Response schema after user deletion.
    
    Attributes:
        user: Deleted user details.
        detail: Success message.
    """
    user: UserResponse
    detail: str = "User deleted successfully"


class UserPatch(BaseModel):
    """Request schema for partial user updates.
    
    All fields are optional. Only provided fields will be updated.
    
    Attributes:
        role: User role ("user" or "admin"). Optional.
        is_active: Account active status. Optional.
        password: New password (min 8 characters). Optional.
    """
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        """Validate role is either 'admin' or 'user'."""
        if v is None:
            return v
        lv = v.lower()
        if lv not in {"admin", "user"}:
            raise ValueError("Role must be either 'admin' or 'user'")
        return lv

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Validate password is at least 8 characters long."""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v
