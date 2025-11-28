from fastapi import FastAPI, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserResponse, UserCreateResponse

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

@app.get("/")
async def root():
    return {"message": "Auth Service API", "version": "0.1.0"}


@app.get("/users", response_model=list[UserResponse])
async def read_users(db: Session = Depends(get_db)):
    users = user_crud.get_users(db)
    return users

@app.post("/users", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.create_user(db, payload)
    return UserCreateResponse(user=UserResponse.model_validate(user))
