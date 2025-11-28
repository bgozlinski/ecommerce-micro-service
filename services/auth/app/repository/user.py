from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password

def create_user(db: Session, user: User) -> User:
    existing_user = db.query(User).filter(User.email == user.email).first()