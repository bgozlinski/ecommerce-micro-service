from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.auth import authenticate_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token, expires_in = authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in
    )
