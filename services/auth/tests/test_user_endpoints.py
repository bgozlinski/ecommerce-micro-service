import os
from typing import Tuple

import pytest

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


def create_user(email: str, password: str, role: str = "user", is_active: bool = True) -> int:
    db = _db_session()
    try:
        u = User(email=email, password_hash=hash_password(password), role=role, is_active=is_active)
        db.add(u)
        db.commit()
        db.refresh(u)
        return u.id
    finally:
        db.close()


def test_register_and_duplicate_email(client):
    payload = {"email": "newuser@example.com", "password": "Password123"}
    r = client.post("/api/v1/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["role"] == "user"
    assert data["user"]["is_active"] is True

    # Duplicate
    r2 = client.post("/api/v1/register", json=payload)
    assert r2.status_code == 400


def test_list_and_get_users(client):
    # Seed two users
    create_user("a@example.com", "Secret1234")
    uid = create_user("b@example.com", "Secret1234")

    r = client.get("/api/v1/users")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 2

    r2 = client.get(f"/api/v1/users/{uid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == uid

    r404 = client.get("/api/v1/users/999999")
    assert r404.status_code == 404


def test_patch_user_role_is_active_and_password_then_delete(client):
    uid = create_user("c@example.com", "OldPassword123")

    # Role to admin
    r = client.patch(f"/api/v1/users/{uid}", json={"role": "admin"})
    assert r.status_code == 200
    assert r.json()["role"] == "admin"

    # Deactivate (block)
    r2 = client.patch(f"/api/v1/users/{uid}", json={"is_active": False})
    assert r2.status_code == 200
    assert r2.json()["is_active"] is False

    # Blocked cannot login
    r_login_blocked = client.post("/api/v1/login", json={"email": "c@example.com", "password": "OldPassword123"})
    assert r_login_blocked.status_code == 403

    # Reactivate and change password
    r3 = client.patch(f"/api/v1/users/{uid}", json={"is_active": True, "password": "NewPassword123"})
    assert r3.status_code == 200
    assert r3.json()["is_active"] is True

    # Login with new password succeeds
    r_login = client.post("/api/v1/login", json={"email": "c@example.com", "password": "NewPassword123"})
    assert r_login.status_code == 200

    # Delete user
    r_del = client.delete(f"/api/v1/users/{uid}")
    assert r_del.status_code == 200

    # Now 404
    r_get = client.get(f"/api/v1/users/{uid}")
    assert r_get.status_code == 404
