from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime


class UserCreateResponse(BaseModel):
    user: UserResponse
    detail: str = "User created successfully"


class UserDeleteResponse(BaseModel):
    user: UserResponse
    detail: str = "User deleted successfully"


class UserPatch(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is None:
            return v
        lv = v.lower()
        if lv not in {"admin", "user"}:
            raise ValueError("Role must be either 'admin' or 'user'")
        return lv

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v
