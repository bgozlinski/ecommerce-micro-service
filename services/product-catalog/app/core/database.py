"""Database configuration and session management for Product Catalog Service.

This module sets up the SQLAlchemy engine, session factory, and declarative base
for ORM models. It provides a dependency function for FastAPI to inject database
sessions into route handlers.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Database session dependency for FastAPI.
    
    Creates a new database session for each request and ensures it's properly
    closed after the request completes, even if an exception occurs.
    
    Yields:
        Session: SQLAlchemy database session.
        
    Example:
        @app.get("/products")
        def get_products(db: Session = Depends(get_db)):
            return db.query(Product).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
