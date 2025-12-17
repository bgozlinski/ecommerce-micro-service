from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User
from app.schemas.user import UserCreate, UserPatch
from app.core.security import hash_password
from fastapi import HTTPException, status

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate) -> User:
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
    user = get_user_by_id(db, user_id)
    if not user:
        return
    db.delete(user)
    db.commit()

def update_user(db: Session, user_id: int, dto: UserPatch) -> Optional[User]:
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
