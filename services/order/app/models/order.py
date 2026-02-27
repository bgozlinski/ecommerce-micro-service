"""SQLAlchemy models for the Order Service.

This module defines models for orders, order items, and shopping cart items.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    """User order record.

    Attributes:
        id: Primary key.
        user_id: ID of the user who placed the order.
        status: Current status of the order (awaiting_payment, paid, failed, cancelled).
        total_amount_cents: Total order amount in cents.
        currency: Currency code (default: PLN).
        created_at: Order creation timestamp.
        paid_at: Timestamp when order was paid.
        cancelled_at: Timestamp when order was cancelled.
        items: Relationship to OrderItem records.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    status = Column(String, nullable=False, default="awaiting_payment")
    total_amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default="PLN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """Individual item within an order.

    Attributes:
        id: Primary key.
        order_id: ID of the parent order.
        product_id: ID of the product.
        quantity: Number of units purchased.
        unit_price_cents: Price per unit at the time of purchase.
        total_price_cents: Total price for this line item.
        order: Relationship to the parent Order record.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price_cents = Column(Integer, nullable=False)
    total_price_cents = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")

class CartItem(Base):
    """Shopping cart item record.

    Attributes:
        id: Primary key.
        user_id: ID of the user who owns the cart.
        product_id: ID of the product in the cart.
        quantity: Number of units in the cart.
        created_at: Timestamp when item was added to cart.
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())