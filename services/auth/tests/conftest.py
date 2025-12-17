import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _ensure_service_root_on_syspath():
    service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if service_root not in sys.path:
        sys.path.insert(0, service_root)


_ensure_service_root_on_syspath()


# Minimal env so Settings.DATABASE_URL can be constructed
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "testdb")


from app.main import app  # noqa: E402
from app.core.database import Base  # noqa: E402
from app.core import database as db_module  # noqa: E402


@pytest.fixture()
def client():
    # In-memory SQLite shared across connections
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Ensure models are imported (if any) before creating schema
    try:
        from app.models import user as _user  # noqa: F401
    except Exception:
        pass

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Swap SessionLocal and override dependency
    original_session_local = db_module.SessionLocal
    db_module.SessionLocal = TestingSessionLocal
    app.dependency_overrides[db_module.get_db] = override_get_db

    try:
        from fastapi.testclient import TestClient

        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.pop(db_module.get_db, None)
        db_module.SessionLocal = original_session_local
