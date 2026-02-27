"""Event handlers for reporting service.

This module contains handlers for different event types received from Kafka,
processing them into aggregated reports and storing raw event data.
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.repositories import report as report_crud

logger = logging.getLogger(__name__)


async def handle_event(event: Dict[str, Any]) -> None:
    """Route event to appropriate handler based on event type.

    Args:
        event: Event payload containing eventType and payload fields.
    """
    event_type = event.get("eventType")
    payload = event.get("payload", {})
    event_id = event.get("eventId")
    timestamp_str = event.get("timestamp")

    if not event_type:
        logger.warning(f"Event without eventType: {event}")
        return

    handlers = {
        "order_created": handle_order_created,
        "order_paid": handle_order_paid,
        "order_failed": handle_order_failed,
        "order_cancelled": handle_order_cancelled,
        "product_created": handle_product_created,
        "product_updated": handle_product_updated,
    }

    handler = handlers.get(event_type)
    if handler:
        try:
            await handler(event_id, timestamp_str, payload)
        except Exception as e:
            logger.error(f"Error handling event {event_type}: {e}", exc_info=True)
    else:
        logger.debug(f"Ignoring event type: {event_type}")


def _parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp string.

    Args:
        timestamp_str: ISO format timestamp.

    Returns:
        datetime: Parsed datetime object.
    """
    if timestamp_str:
        try:
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            pass
    return datetime.now(timezone.utc)


async def handle_order_created(event_id: str, timestamp_str: str, payload: Dict[str, Any]) -> None:
    """Handle order_created event - update daily sales order count.

    Args:
        event_id: Unique event identifier.
        timestamp_str: Event timestamp string.
        payload: Event payload containing orderId, userId, totalAmount.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")

    if not order_id or not user_id:
        logger.warning(f"Missing orderId or userId in order_created event: {payload}")
        return

    logger.info(f"Handling order_created for orderId={order_id}")

    event_timestamp = _parse_timestamp(timestamp_str)
    report_date = event_timestamp.date()

    db = SessionLocal()
    try:
        saved = report_crud.save_order_event(
            db, event_id, "order_created", order_id, user_id,
            None, "PLN", event_timestamp
        )

        if saved:
            report_crud.get_or_create_daily_report(db, report_date)
            # We need a method to increment total_orders without incrementing paid ones
            report = report_crud.get_or_create_daily_report(db, report_date)
            report.total_orders += 1
            db.commit()
            logger.info(f"Daily report updated for {report_date}: +1 total order")
        else:
            logger.info(f"Duplicate event {event_id} - skipping aggregation")

    except Exception as e:
        logger.error(f"Error handling order_created: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_failed(event_id: str, timestamp_str: str, payload: Dict[str, Any]) -> None:
    """Handle order_failed event - store event.

    Args:
        event_id: Unique event identifier.
        timestamp_str: Event timestamp string.
        payload: Event payload containing orderId, userId.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")

    if not order_id or not user_id:
        return

    event_timestamp = _parse_timestamp(timestamp_str)

    db = SessionLocal()
    try:
        report_crud.save_order_event(
            db, event_id, "order_failed", order_id, user_id,
            None, "PLN", event_timestamp
        )
    except Exception as e:
        logger.error(f"Error handling order_failed: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_paid(event_id: str, timestamp_str: str, payload: Dict[str, Any]) -> None:
    """Handle order_paid event - update daily sales and store event.

    Args:
        event_id: Unique event identifier.
        timestamp_str: Event timestamp string.
        payload: Event payload containing orderId, userId, totalAmount.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")
    total_amount = payload.get("totalAmount", 0)

    if not order_id or not user_id:
        logger.warning(f"Missing orderId or userId in order_paid event: {payload}")
        return

    logger.info(f"Handling order_paid for orderId={order_id}, amount={total_amount}")

    event_timestamp = _parse_timestamp(timestamp_str)
    report_date = event_timestamp.date()

    db = SessionLocal()
    try:
        # Save raw event (idempotent)
        saved = report_crud.save_order_event(
            db, event_id, "order_paid", order_id, user_id,
            total_amount, "PLN", event_timestamp
        )

        # Only update aggregates if event is new (not duplicate)
        if saved:
            report_crud.increment_daily_paid(db, report_date, total_amount)
            logger.info(f"Daily report updated for {report_date}: +{total_amount} cents")
        else:
            logger.info(f"Duplicate event {event_id} - skipping aggregation")

    except Exception as e:
        logger.error(f"Error handling order_paid: {e}", exc_info=True)
    finally:
        db.close()


async def handle_order_cancelled(event_id: str, timestamp_str: str, payload: Dict[str, Any]) -> None:
    """Handle order_cancelled event - update daily cancellation count.

    Args:
        event_id: Unique event identifier.
        timestamp_str: Event timestamp string.
        payload: Event payload containing orderId, userId.
    """
    order_id = payload.get("orderId")
    user_id = payload.get("userId")

    if not order_id or not user_id:
        logger.warning(f"Missing orderId or userId in order_cancelled event: {payload}")
        return

    logger.info(f"Handling order_cancelled for orderId={order_id}")

    event_timestamp = _parse_timestamp(timestamp_str)
    report_date = event_timestamp.date()

    db = SessionLocal()
    try:
        saved = report_crud.save_order_event(
            db, event_id, "order_cancelled", order_id, user_id,
            None, "PLN", event_timestamp
        )

        if saved:
            report_crud.increment_daily_cancelled(db, report_date)
            logger.info(f"Daily report updated for {report_date}: +1 cancelled")
        else:
            logger.info(f"Duplicate event {event_id} - skipping aggregation")

    except Exception as e:
        logger.error(f"Error handling order_cancelled: {e}", exc_info=True)
    finally:
        db.close()


async def handle_product_created(event_id: str, timestamp_str: str, payload: Dict[str, Any]) -> None:
    """Handle product_created event - store product event for tracking.

    Args:
        event_id: Unique event identifier.
        timestamp_str: Event timestamp string.
        payload: Event payload containing productId, name, price.
    """
    product_id = payload.get("productId")
    product_name = payload.get("name")
    price_cents = payload.get("price")

    logger.info(f"Handling product_created for productId={product_id}")

    event_timestamp = _parse_timestamp(timestamp_str)

    db = SessionLocal()
    try:
        report_crud.save_product_event(
            db, event_id, "product_created", product_id,
            product_name, price_cents, event_timestamp
        )
    except Exception as e:
        logger.error(f"Error handling product_created: {e}", exc_info=True)
    finally:
        db.close()


async def handle_product_updated(event_id: str, timestamp_str: str, payload: Dict[str, Any]) -> None:
    """Handle product_updated event - store product event for tracking.

    Args:
        event_id: Unique event identifier.
        timestamp_str: Event timestamp string.
        payload: Event payload containing productId, changes.
    """
    product_id = payload.get("productId")

    logger.info(f"Handling product_updated for productId={product_id}")

    event_timestamp = _parse_timestamp(timestamp_str)

    db = SessionLocal()
    try:
        report_crud.save_product_event(
            db, event_id, "product_updated", product_id,
            None, None, event_timestamp
        )
    except Exception as e:
        logger.error(f"Error handling product_updated: {e}", exc_info=True)
    finally:
        db.close()
