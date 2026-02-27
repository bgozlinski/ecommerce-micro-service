"""SQLAlchemy models for the Inventory Service.

This module defines models for tracking product stock levels and
individual digital license keys.
"""

from app.core.database import Base
from sqlalchemy import Column, Integer, String, func, DateTime

class Inventory(Base):
    """Inventory summary for a product.

    Attributes:
        id: Primary key.
        product_id: ID of the product.
        available_qty: Number of keys available for sale.
        reserved_qty: Number of keys reserved for pending orders.
        updated_at: Timestamp of the last update.
    """
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    available_qty = Column(Integer, nullable=False)
    reserved_qty = Column(Integer, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ProductKeys(Base):
    """Digital license key record.

    Attributes:
        id: Primary key.
        product_id: ID of the product this key belongs to.
        key_value: The unique license key string.
        status: Current state of the key (available, reserved, assigned).
        order_item_id: ID of the order item this key is assigned to.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
    """
    __tablename__ = "product_keys"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, nullable=False)
    key_value = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="available")
    order_item_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
