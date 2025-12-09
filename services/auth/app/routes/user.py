from http.client import responses

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse, UserDeleteResponse
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.get("/users", response_model=list[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    users = user_crud.get_users(db)
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.delete("/users/{user_id}",response_model=UserDeleteResponse, status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_crud.delete_user(db, user_id)
    return  UserDeleteResponse(user=UserResponse.model_validate(user))

@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.create_user(db=db, user=user_create)
    return UserCreateResponse(user=UserResponse.model_validate(user))
