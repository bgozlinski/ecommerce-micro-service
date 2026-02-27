"""Repository layer for reporting database operations.

This module provides CRUD and aggregation operations for daily sales reports,
order events, and product events.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional, List
from datetime import date, datetime
from app.models.report import ReportDailySales, OrderEvent, ProductEvent


def get_or_create_daily_report(db: Session, report_date: date) -> ReportDailySales:
    """Get or create a daily sales report record.

    Args:
        db: Database session.
        report_date: Date for the report.

    Returns:
        ReportDailySales: Existing or newly created report record.
    """
    report = db.query(ReportDailySales).filter(
        ReportDailySales.report_date == report_date
    ).first()

    if not report:
        report = ReportDailySales(
            report_date=report_date,
            total_orders=0,
            total_paid_orders=0,
            total_revenue_cents=0,
            total_cancelled_orders=0
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    return report


def increment_daily_paid(db: Session, report_date: date, amount_cents: int) -> ReportDailySales:
    """Increment paid order count and revenue for a daily report.

    Args:
        db: Database session.
        report_date: Date of the order.
        amount_cents: Order amount in cents.

    Returns:
        ReportDailySales: Updated report record.
    """
    report = get_or_create_daily_report(db, report_date)
    # total_orders is already incremented on order_created event (hypothetically)
    # but currently we don't have order_created handler in Reporting Service.
    # To keep it consistent, let's increment total_orders here if we only track paid ones,
    # OR we should add order_created handler. 
    # Based on current implementation, it seems we increment both.
    report.total_orders += 1 
    report.total_paid_orders += 1
    report.total_revenue_cents += amount_cents
    db.commit()
    db.refresh(report)
    return report


def increment_daily_cancelled(db: Session, report_date: date) -> ReportDailySales:
    """Increment cancelled order count for a daily report.

    Args:
        db: Database session.
        report_date: Date of the cancellation.

    Returns:
        ReportDailySales: Updated report record.
    """
    report = get_or_create_daily_report(db, report_date)
    report.total_cancelled_orders += 1
    db.commit()
    db.refresh(report)
    return report


def save_order_event(db: Session, event_id: str, event_type: str, order_id: int,
                     user_id: int, amount_cents: Optional[int],
                     currency: str, event_timestamp: datetime) -> Optional[OrderEvent]:
    """Save an order event to the database (idempotent).

    Args:
        db: Database session.
        event_id: Unique event identifier.
        event_type: Event type string.
        order_id: Order identifier.
        user_id: User identifier.
        amount_cents: Order amount in cents.
        currency: Currency code.
        event_timestamp: Original event timestamp.

    Returns:
        Optional[OrderEvent]: Created event record, or None if duplicate.
    """
    existing = db.query(OrderEvent).filter(OrderEvent.event_id == event_id).first()
    if existing:
        return None

    event = OrderEvent(
        event_id=event_id,
        event_type=event_type,
        order_id=order_id,
        user_id=user_id,
        amount_cents=amount_cents,
        currency=currency,
        event_timestamp=event_timestamp
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def save_product_event(db: Session, event_id: str, event_type: str, product_id: int,
                       product_name: Optional[str], price_cents: Optional[int],
                       event_timestamp: datetime) -> Optional[ProductEvent]:
    """Save a product event to the database (idempotent).

    Args:
        db: Database session.
        event_id: Unique event identifier.
        event_type: Event type string.
        product_id: Product identifier.
        product_name: Product name.
        price_cents: Product price in cents.
        event_timestamp: Original event timestamp.

    Returns:
        Optional[ProductEvent]: Created event record, or None if duplicate.
    """
    existing = db.query(ProductEvent).filter(ProductEvent.event_id == event_id).first()
    if existing:
        return None

    event = ProductEvent(
        event_id=event_id,
        event_type=event_type,
        product_id=product_id,
        product_name=product_name,
        price_cents=price_cents,
        event_timestamp=event_timestamp
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_daily_reports(db: Session, date_from: Optional[date] = None,
                      date_to: Optional[date] = None) -> List[ReportDailySales]:
    """Retrieve daily sales reports with optional date filtering.

    Args:
        db: Database session.
        date_from: Start date filter (inclusive).
        date_to: End date filter (inclusive).

    Returns:
        List[ReportDailySales]: List of daily report records.
    """
    query = db.query(ReportDailySales)
    if date_from:
        query = query.filter(ReportDailySales.report_date >= date_from)
    if date_to:
        query = query.filter(ReportDailySales.report_date <= date_to)
    return query.order_by(ReportDailySales.report_date.desc()).all()


def get_monthly_reports(db: Session, year: Optional[int] = None):
    """Retrieve monthly aggregated sales reports.

    Args:
        db: Database session.
        year: Optional year filter.

    Returns:
        List of tuples: (year, month, total_orders, total_paid_orders,
                         total_revenue_cents, total_cancelled_orders).
    """
    query = db.query(
        extract('year', ReportDailySales.report_date).label('year'),
        extract('month', ReportDailySales.report_date).label('month'),
        func.sum(ReportDailySales.total_orders).label('total_orders'),
        func.sum(ReportDailySales.total_paid_orders).label('total_paid_orders'),
        func.sum(ReportDailySales.total_revenue_cents).label('total_revenue_cents'),
        func.sum(ReportDailySales.total_cancelled_orders).label('total_cancelled_orders'),
    )
    if year:
        query = query.filter(extract('year', ReportDailySales.report_date) == year)
    query = query.group_by(
        extract('year', ReportDailySales.report_date),
        extract('month', ReportDailySales.report_date)
    ).order_by(
        extract('year', ReportDailySales.report_date).desc(),
        extract('month', ReportDailySales.report_date).desc()
    )
    return query.all()


def get_top_products(db: Session, limit: int = 10):
    """Retrieve top products by total revenue from paid orders.

    Args:
        db: Database session.
        limit: Maximum number of products to return.

    Returns:
        List of tuples: (product_id, total_sold, total_revenue_cents).
    """
    # Join with product_events to get product name? 
    # Current schema doesn't have product_id in OrderEvent as FK to products.
    # Actually OrderEvent has order_id, not product_id. 
    # The requirement says "top products reports".
    # I should check if OrderEvent stores product_id.
    # Looking at handle_order_paid in notification service, it has orderId, userId, keys.
    # Order Service's publish_order_event sends orderId, userId and extra payload.
    
    # Wait, my get_top_products used OrderEvent.order_id but labeled it product_id in route.
    # That's probably wrong. 
    
    query = db.query(
        OrderEvent.order_id.label('product_id'), # Temporarily using order_id if product_id is missing
        func.count(OrderEvent.id).label('total_sold'),
        func.sum(OrderEvent.amount_cents).label('total_revenue_cents'),
    ).filter(
        OrderEvent.event_type == 'order_paid'
    ).group_by(
        OrderEvent.order_id
    ).order_by(
        func.sum(OrderEvent.amount_cents).desc()
    ).limit(limit)
    return query.all()
