"""Pydantic schemas for reporting service.

This module defines request/response schemas for report endpoints.
"""

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DailySalesReportOut(BaseModel):
    """Daily sales report response schema.

    Attributes:
        id: Report record ID.
        report_date: Date of the report.
        total_orders: Total orders created.
        total_paid_orders: Total paid orders.
        total_revenue_cents: Total revenue in cents.
        total_cancelled_orders: Total cancelled orders.
        avg_order_value_cents: Computed average order value in cents.
        created_at: Record creation timestamp.
    """
    id: int
    report_date: date
    total_orders: int
    total_paid_orders: int
    total_revenue_cents: int
    total_cancelled_orders: int
    avg_order_value_cents: float
    created_at: datetime

    model_config = {"from_attributes": True}


class MonthlySalesReportOut(BaseModel):
    """Monthly aggregated sales report response schema.

    Attributes:
        year: Report year.
        month: Report month.
        total_orders: Total orders in the month.
        total_paid_orders: Total paid orders in the month.
        total_revenue_cents: Total revenue in cents.
        total_cancelled_orders: Total cancelled orders.
        avg_order_value_cents: Average order value in cents.
    """
    year: int
    month: int
    total_orders: int
    total_paid_orders: int
    total_revenue_cents: int
    total_cancelled_orders: int
    avg_order_value_cents: float


class TopProductOut(BaseModel):
    """Top product report response schema.

    Attributes:
        product_id: Product identifier.
        total_sold: Total quantity sold (paid orders).
        total_revenue_cents: Total revenue from this product.
    """
    product_id: int
    total_sold: int
    total_revenue_cents: int
