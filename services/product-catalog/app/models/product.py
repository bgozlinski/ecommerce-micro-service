"""SQLAlchemy models for the Product Catalog Service.

This module defines the Product model representing game keys and licenses
available for sale in the platform.
"""

from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, Text, func, DateTime

class Product(Base):
    """Product model for game keys and licenses.

    Attributes:
        id: Primary key.
        name: Name of the product (game title).
        description: Detailed product description.
        price_cents: Product price in cents.
        currency: Currency code (default: PLN).
        category: Product category (e.g., Action, RPG).
        platform: Target platform (e.g., Steam, Origin).
        is_active: Status flag (active/inactive).
        created_at: Record creation timestamp.
        updated_at: Record last update timestamp.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="PLN")
    category = Column(String)
    platform = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True))