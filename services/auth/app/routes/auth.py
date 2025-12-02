from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud.user import get_user_by_email
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })

    expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expiration
    )