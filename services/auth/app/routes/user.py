from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.get("/users", response_model=list[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    users = user_crud.get_users(db)
    return users

@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.create_user(db=db, user=user_create)
    return UserCreateResponse(user=UserResponse.model_validate(user))
