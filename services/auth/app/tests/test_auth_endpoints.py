import os
from typing import Tuple

os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "testdb")

from app.core import database as db_module  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User  # noqa: E402


def _db_session():
    TestingSessionLocal = db_module.SessionLocal
    return TestingSessionLocal()


def seed_user(email: str, password: str, is_active: bool = True, role: str = "user") -> Tuple[int, str]:
    db = _db_session()
    try:
        u = User(email=email, password_hash=hash_password(password), is_active=is_active, role=role)
        db.add(u)
        db.commit()
        db.refresh(u)
        return u.id, u.email
    finally:
        db.close()


def test_login_success(client):
    # Arrange
    email = "john@example.com"
    password = "StrongPass123"
    seed_user(email, password, is_active=True)

    # Act
    r = client.post("/api/v1/login", json={"email": email, "password": password})

    # Assert
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body and isinstance(body["access_token"], str) and len(body["access_token"]) > 0
    assert body["token_type"] == "bearer"
    assert isinstance(body["expires_in"], int) and body["expires_in"] > 0


def test_login_wrong_password_unauthorized(client):
    email = "alice@example.com"
    password = "CorrectHorseBatteryStaple"
    seed_user(email, password)

    r = client.post("/api/v1/login", json={"email": email, "password": "wrongpass"})
    assert r.status_code == 401


def test_login_inactive_forbidden(client):
    email = "bob@example.com"
    password = "AnotherStrongP@ss"
    seed_user(email, password, is_active=False)

    r = client.post("/api/v1/login", json={"email": email, "password": password})
    assert r.status_code == 403
