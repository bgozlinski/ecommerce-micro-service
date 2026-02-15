"""User management API endpoints.

This module defines REST API routes for user management operations, including
user registration, retrieval, updates, and deletion.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse, UserDeleteResponse, UserPatch
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.get("/users", response_model=list[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    """Retrieve a list of all users.
    
    Args:
        db: Database session dependency.
        
    Returns:
        list[UserResponse]: List of all users in the system.
    """
    users = user_crud.get_users(db)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific user by ID.
    
    Args:
        user_id: User identifier.
        db: Database session dependency.
        
    Returns:
        UserResponse: User details.
        
    Raises:
        HTTPException: 404 if user not found.
    """
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.delete("/users/{user_id}",response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user account.
    
    Args:
        user_id: User identifier.
        db: Database session dependency.
        
    Returns:
        UserDeleteResponse: Deleted user details.
        
    Raises:
        HTTPException: 404 if user not found.
    """
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_crud.delete_user(db, user_id)
    return  UserDeleteResponse(user=UserResponse.model_validate(user))

@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account.
    
    Creates a new user with the provided email and password. The password is
    automatically hashed before storage.
    
    Args:
        user_create: User registration data (email and password).
        db: Database session dependency.
        
    Returns:
        UserCreateResponse: Created user details.
        
    Raises:
        HTTPException: 400 if email is already registered.
    """
    user = user_crud.create_user(db=db, user=user_create)
    return UserCreateResponse(user=UserResponse.model_validate(user))

@router.patch("/users/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, dto: UserPatch, db: Session = Depends(get_db)):
    """Update user account details.
    
    Allows partial updates to user account (role, active status, password).
    Only provided fields are updated.
    
    Args:
        user_id: User identifier.
        dto: User update data (role, is_active, password).
        db: Database session dependency.
        
    Returns:
        UserResponse: Updated user details.
        
    Raises:
        HTTPException: 404 if user not found.
    """
    updated = user_crud.update_user(db, user_id, dto)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(updated)
