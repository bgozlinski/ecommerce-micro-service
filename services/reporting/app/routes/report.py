"""Reporting API endpoints.

This module defines REST API routes for retrieving sales reports,
including daily, monthly, top products, and CSV/JSON export.
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import report as report_crud
from app.schemas.report import DailySalesReportOut, MonthlySalesReportOut, TopProductOut
from app.core.config import settings
from typing import Optional, List
from datetime import date
import csv
import io
import json

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/reports", tags=["reports"])


@router.get("/daily", response_model=List[DailySalesReportOut])
def get_daily_reports(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieve daily sales reports.

    Args:
        date_from: Start date filter (inclusive).
        date_to: End date filter (inclusive).
        db: Database session dependency.

    Returns:
        List[DailySalesReportOut]: List of daily sales reports.
    """
    reports = report_crud.get_daily_reports(db, date_from, date_to)
    return [
        DailySalesReportOut(
            id=r.id,
            report_date=r.report_date,
            total_orders=r.total_orders,
            total_paid_orders=r.total_paid_orders,
            total_revenue_cents=r.total_revenue_cents,
            total_cancelled_orders=r.total_cancelled_orders,
            avg_order_value_cents=(
                r.total_revenue_cents / r.total_paid_orders if r.total_paid_orders > 0 else 0
            ),
            created_at=r.created_at,
        )
        for r in reports
    ]


@router.get("/monthly", response_model=List[MonthlySalesReportOut])
def get_monthly_reports(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """Retrieve monthly aggregated sales reports.

    Args:
        year: Optional year filter.
        db: Database session dependency.

    Returns:
        List[MonthlySalesReportOut]: List of monthly sales reports.
    """
    rows = report_crud.get_monthly_reports(db, year)
    return [
        MonthlySalesReportOut(
            year=int(r.year),
            month=int(r.month),
            total_orders=r.total_orders,
            total_paid_orders=r.total_paid_orders,
            total_revenue_cents=r.total_revenue_cents,
            total_cancelled_orders=r.total_cancelled_orders,
            avg_order_value_cents=(
                r.total_revenue_cents / r.total_paid_orders if r.total_paid_orders > 0 else 0
            ),
        )
        for r in rows
    ]


@router.get("/top-products", response_model=List[TopProductOut])
def get_top_products(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Retrieve top products by revenue.

    Args:
        limit: Maximum number of products to return.
        db: Database session dependency.

    Returns:
        List[TopProductOut]: List of top products.
    """
    rows = report_crud.get_top_products(db, limit)
    return [
        TopProductOut(
            product_id=r.product_id,
            total_sold=r.total_sold,
            total_revenue_cents=r.total_revenue_cents or 0,
        )
        for r in rows
    ]


@router.get("/export/daily")
def export_daily_reports(
    format: str = Query("json", pattern="^(json|csv)$"),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Export daily sales reports in JSON or CSV format.

    Args:
        format: Export format ('json' or 'csv').
        date_from: Start date filter (inclusive).
        date_to: End date filter (inclusive).
        db: Database session dependency.

    Returns:
        StreamingResponse: File download response.
    """
    reports = report_crud.get_daily_reports(db, date_from, date_to)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "report_date", "total_orders", "total_paid_orders",
            "total_revenue_cents", "total_cancelled_orders", "avg_order_value_cents"
        ])
        for r in reports:
            avg = r.total_revenue_cents / r.total_paid_orders if r.total_paid_orders > 0 else 0
            writer.writerow([
                r.report_date.isoformat(), r.total_orders, r.total_paid_orders,
                r.total_revenue_cents, r.total_cancelled_orders, round(avg, 2)
            ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=daily_reports.csv"}
        )

    # JSON export
    data = []
    for r in reports:
        avg = r.total_revenue_cents / r.total_paid_orders if r.total_paid_orders > 0 else 0
        data.append({
            "report_date": r.report_date.isoformat(),
            "total_orders": r.total_orders,
            "total_paid_orders": r.total_paid_orders,
            "total_revenue_cents": r.total_revenue_cents,
            "total_cancelled_orders": r.total_cancelled_orders,
            "avg_order_value_cents": round(avg, 2),
        })
    json_output = json.dumps(data, ensure_ascii=False, indent=2)
    return StreamingResponse(
        iter([json_output]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=daily_reports.json"}
    )
