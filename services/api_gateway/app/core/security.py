"""Security utilities for the API Gateway.

This module provides helpers for password hashing/verification (for completeness)
and JWT encoding/decoding. Note: Per the project guidelines, JWTs are issued by
the Auth Service; the gateway primarily verifies/decodes tokens and forwards
user context via `X-User-Id` and `X-User-Role` headers.
"""

from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Hash a plaintext password using Passlib's `CryptContext`.

    Args:
        password: Plaintext password to hash.

    Returns:
        A salted, secure hash of the password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash.

    Args:
        plain_password: User-provided plaintext password.
        hashed_password: Password hash retrieved from storage.

    Returns:
        True if the plaintext password matches the hash; otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """Create a signed JWT access token.

    Note:
        In this architecture, tokens should be issued by the Auth Service.
        This utility is provided for completeness and testing.

    Args:
        data: Claims to embed in the token (e.g., `{"sub": user_id, "role": "user"}`).
        expires_delta: Optional custom TTL in minutes. If not provided,
            `settings.ACCESS_TOKEN_EXPIRE_MINUTES` is used.

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(timezone.utc)
    minutes = expires_delta if expires_delta is not None else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = now + timedelta(minutes=minutes)

    to_encode = {**data, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}

    encoded_jwt  = jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token.

    Args:
        token: Bearer token string (without the `Bearer ` prefix).

    Returns:
        Decoded JWT payload as a dictionary.

    Raises:
        ExpiredSignatureError: If the token is well-formed but expired.
        InvalidTokenError: If the token signature or structure is invalid.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError as e:
        raise e
    except InvalidTokenError as e:
        raise e
