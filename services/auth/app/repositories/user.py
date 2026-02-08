"""Repository layer for user database operations.

This module provides CRUD operations for user management, including user
creation, retrieval, updates, and deletion.
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserPatch
from app.core.security import hash_password
from fastapi import HTTPException, status

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by their ID.
    
    Args:
        db: Database session.
        user_id: User identifier.
        
    Returns:
        Optional[User]: User record if found, None otherwise.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user by their email address.
    
    Args:
        db: Database session.
        email: User's email address.
        
    Returns:
        Optional[User]: User record if found, None otherwise.
    """
    return db.query(User).filter(User.email == email).first()

def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100
) -> List[User]:
    """Retrieve a paginated list of users.
    
    Args:
        db: Database session.
        skip: Number of records to skip (offset). Defaults to 0.
        limit: Maximum number of records to return. Defaults to 100.
        
    Returns:
        List[User]: List of user records.
    """
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user account.
    
    Hashes the password and creates a new user record. Validates that the
    email is not already registered.
    
    Args:
        db: Database session.
        user: User creation data (email and password).
        
    Returns:
        User: Newly created user record.
        
    Raises:
        HTTPException: 400 if email is already registered.
    """
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def delete_user(db: Session, user_id: int) -> None:
    """Delete a user account.
    
    Args:
        db: Database session.
        user_id: User identifier.
        
    Notes:
        Silently succeeds if user doesn't exist.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return
    db.delete(user)
    db.commit()

def update_user(db: Session, user_id: int, dto: UserPatch) -> Optional[User]:
    """Update user account details.
    
    Allows updating role, active status, and password. Only provided fields
    are updated (partial update).
    
    Args:
        db: Database session.
        user_id: User identifier.
        dto: User update data (role, is_active, password).
        
    Returns:
        Optional[User]: Updated user record if found, None otherwise.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    if dto.role is not None:
        user.role = dto.role
    if dto.is_active is not None:
        user.is_active = dto.is_active
    if dto.password is not None:
        user.password_hash = hash_password(dto.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
