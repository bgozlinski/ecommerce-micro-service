"""Database models for reporting service.

This module defines SQLAlchemy models for daily sales reports
and order event tracking used for aggregation.
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.core.database import Base


class ReportDailySales(Base):
    """Aggregated daily sales data.

    Stores pre-computed daily sales metrics including order counts,
    revenue totals, and average order values.

    Attributes:
        id: Primary key.
        report_date: Date of the report (unique, indexed).
        total_orders: Total number of orders created on this date.
        total_paid_orders: Number of successfully paid orders.
        total_revenue_cents: Total revenue in cents from paid orders.
        total_cancelled_orders: Number of cancelled orders.
        created_at: Timestamp when report record was created.
    """
    __tablename__ = "reports_daily_sales"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False, unique=True, index=True)
    total_orders = Column(Integer, nullable=False, default=0)
    total_paid_orders = Column(Integer, nullable=False, default=0)
    total_revenue_cents = Column(Integer, nullable=False, default=0)
    total_cancelled_orders = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OrderEvent(Base):
    """Raw order event log for reporting purposes.

    Stores individual order events received from Kafka for detailed
    analysis and report generation.

    Attributes:
        id: Primary key.
        event_id: Unique event identifier from Kafka.
        event_type: Type of event (order_paid, order_cancelled, etc.).
        order_id: Order identifier.
        user_id: User identifier.
        amount_cents: Order amount in cents (if applicable).
        currency: Currency code (default PLN).
        event_timestamp: Original event timestamp.
        created_at: Timestamp when record was stored.
    """
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False, unique=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    amount_cents = Column(Integer, nullable=True)
    currency = Column(String(3), nullable=False, default="PLN")
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ProductEvent(Base):
    """Raw product event log for reporting purposes.

    Stores product lifecycle events for tracking catalog changes.

    Attributes:
        id: Primary key.
        event_id: Unique event identifier from Kafka.
        event_type: Type of event (product_created, product_updated).
        product_id: Product identifier.
        product_name: Product name (if available).
        price_cents: Product price in cents (if available).
        event_timestamp: Original event timestamp.
        created_at: Timestamp when record was stored.
    """
    __tablename__ = "product_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, nullable=False, unique=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    product_name = Column(String, nullable=True)
    price_cents = Column(Integer, nullable=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
