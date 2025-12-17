import os
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker


os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "testdb")


from app.main import app
from app.core.database import Base
from app.core import database as db_module
from app.models.product import Product


@pytest.fixture()
def client():
    # In-memory SQLite engine
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create schema
    Base.metadata.create_all(bind=engine)

    # Override DB dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Swap SessionLocal used elsewhere (e.g., repo direct usage)
    original_session_local = db_module.SessionLocal
    db_module.SessionLocal = TestingSessionLocal
    app.dependency_overrides[db_module.get_db] = override_get_db

    try:
        with TestClient(app) as c:
            yield c
    finally:
        # Cleanup overrides
        app.dependency_overrides.pop(db_module.get_db, None)
        db_module.SessionLocal = original_session_local


def seed_products(session):
    now = datetime.utcnow()
    rows = [
        Product(name="Witcher 3", description="RPG game", price_cents=1099, currency="PLN", category="RPG", platform="Steam", is_active=True, created_at=now - timedelta(days=3)),
        Product(name="Cyberpunk 2077", description="Sci-fi RPG", price_cents=1599, currency="PLN", category="RPG", platform="GOG", is_active=True, created_at=now - timedelta(days=2)),
        Product(name="FIFA 24", description="Football", price_cents=2599, currency="PLN", category="Sports", platform="Origin", is_active=True, created_at=now - timedelta(days=1)),
        Product(name="Old Game", description="classic", price_cents=499, currency="PLN", category="Retro", platform="Steam", is_active=False, created_at=now - timedelta(days=10)),
    ]
    session.add_all(rows)
    session.commit()
    for r in rows:
        session.refresh(r)
    return rows


def get_db_from_client(client):
    # Access the overridden SessionLocal via db_module
    TestingSessionLocal = db_module.SessionLocal
    return TestingSessionLocal()


def test_list_products_default_returns_only_active_sorted_desc(client):
    db = get_db_from_client(client)
    try:
        seed_products(db)
    finally:
        db.close()

    resp = client.get("/api/v1/products")
    assert resp.status_code == 200
    data = resp.json()
    # Should not include inactive "Old Game"
    names = [p["name"] for p in data]
    assert "Old Game" not in names
    # Sorted by created_at desc -> newest first: FIFA 24, Cyberpunk 2077, Witcher 3
    assert names == ["FIFA 24", "Cyberpunk 2077", "Witcher 3"]


def test_filter_by_category_platform_and_price_and_search(client):
    db = get_db_from_client(client)
    try:
        seed_products(db)
    finally:
        db.close()

    # Category + platform
    r = client.get("/api/v1/products", params={"category": "RPG", "platform": "GOG"})
    assert r.status_code == 200
    names = [p["name"] for p in r.json()]
    assert names == ["Cyberpunk 2077"]

    # Price range
    r = client.get("/api/v1/products", params={"min_price_cents": 1500, "max_price_cents": 3000})
    assert r.status_code == 200
    names = [p["name"] for p in r.json()]
    assert names == ["FIFA 24", "Cyberpunk 2077"]

    # Search (case-insensitive) in name/description
    r = client.get("/api/v1/products", params={"search": "rpg"})
    assert r.status_code == 200
    names = [p["name"] for p in r.json()]
    assert set(names) == {"Witcher 3", "Cyberpunk 2077"}


def test_sorting_and_pagination(client):
    db = get_db_from_client(client)
    try:
        seed_products(db)
    finally:
        db.close()

    # Sort by price asc
    r = client.get("/api/v1/products", params={"sort_by": "price_cents", "sort_dir": "asc"})
    assert r.status_code == 200
    prices = [p["price_cents"] for p in r.json()]
    assert prices == sorted(prices)

    # Pagination limit and skip
    r = client.get("/api/v1/products", params={"limit": 1})
    assert r.status_code == 200
    assert len(r.json()) == 1

    r2 = client.get("/api/v1/products", params={"skip": 1, "limit": 1})
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    # Different item than first page
    assert r.json()[0]["id"] != r2.json()[0]["id"]


def test_get_product_by_id_200_and_404(client):
    db = get_db_from_client(client)
    try:
        items = seed_products(db)
        pid = items[0].id
    finally:
        db.close()

    r = client.get(f"/api/v1/products/{pid}")
    assert r.status_code == 200
    assert r.json()["id"] == pid

    r404 = client.get("/api/v1/products/99999")
    assert r404.status_code == 404


def test_create_update_delete_product_flow(client):
    # Create
    payload = {
        "name": "New Game",
        "description": "desc",
        "price_cents": 1234,
        "currency": "PLN",
        "category": "Indie",
        "platform": "Steam",
        "is_active": True,
    }
    r = client.post("/api/v1/products", json=payload)
    assert r.status_code == 201
    created = r.json()
    pid = created["id"]
    assert created["name"] == "New Game"

    # Update (patch)
    upd = {"price_cents": 1500, "is_active": False}
    r2 = client.patch(f"/api/v1/products/{pid}", json=upd)
    assert r2.status_code == 200
    body = r2.json()
    assert body["price_cents"] == 1500
    assert body["is_active"] is False
    assert body.get("updated_at") is not None

    # Delete (should 204 and keep record but inactive)
    r3 = client.delete(f"/api/v1/products/{pid}")
    assert r3.status_code == 204

    # After delete it should be inactive when fetched from list (if included)
    r4 = client.get("/api/v1/products", params={"is_active": False})
    assert r4.status_code == 200
    ids = [p["id"] for p in r4.json()]
    assert pid in ids
