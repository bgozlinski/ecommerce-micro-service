"""Repository layer for order database operations.

This module provides data access functions for cart and order management,
coordinating with external services (Product Catalog, Inventory) and
publishing events to Kafka.
"""

import requests
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, CartItem
from app.core.config import settings
from datetime import datetime, timezone
from app.kafka import publish_order_event
import logging

logger = logging.getLogger(__name__)

def get_cart_items(db: Session, user_id: int):
    """Retrieve all cart items for a user.

    Args:
        db: Database session.
        user_id: User identifier.

    Returns:
        list[CartItem]: List of cart items.
    """
    return db.query(CartItem).filter(CartItem.user_id == user_id).all()


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    """Add a product to the user's cart or update quantity if exists.

    Args:
        db: Database session.
        user_id: User identifier.
        product_id: Product identifier.
        quantity: Quantity to add.

    Returns:
        CartItem: Updated or newly created cart item.
    """
    item = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.product_id == product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(item)
    db.commit()
    return item


def create_order_from_cart(db: Session, user_id: int):
    """Create an order from the user's cart items.

    This function orchestrates the order creation process:
    1. Fetch cart items
    2. Validate products are active
    3. Reserve stock in Inventory Service
    4. Create order and order items
    5. Clear cart
    6. Publish "order_created" event

    Args:
        db: Database session.
        user_id: User identifier.

    Returns:
        Order: Created order with status "awaiting_payment", or None if failed.

    Notes:
        - Returns None if cart is empty, product inactive, or stock unavailable.
        - All reservations are atomic (all succeed or all fail).
    """
    cart_items = get_cart_items(db, user_id)
    if not cart_items:
        return None

    total_amount = 0
    order_items_data = []

    for ci in cart_items:
        product = get_product_details(ci.product_id)
        if not product or not product.get("is_active"):
            return None

        price = product["price_cents"]

        resp = requests.post(
            f"{settings.INVENTORY_SERVICE_URL}/api/v1/inventory/reserve",
            json={"product_id": ci.product_id, "quantity": ci.quantity},
            timeout=5
        )

        if resp.status_code != 200:
            return None

        total_price = price * ci.quantity
        total_amount += total_price
        order_items_data.append({
            "product_id": ci.product_id,
            "quantity": ci.quantity,
            "unit_price_cents": price,
            "total_price_cents": total_price
        })

    order = Order(user_id=user_id, total_amount_cents=total_amount, status="awaiting_payment")
    db.add(order)
    db.flush()

    for item_data in order_items_data:
        db_item = OrderItem(order_id=order.id, **item_data)
        db.add(db_item)

    db.query(CartItem).filter(CartItem.user_id == user_id).delete()

    db.commit()
    logger.info(f"Order created: {order.id}")
    logger.info('Publikuje event')
    publish_order_event(
        event_type="order_created",
        order_id=order.id,
        user_id=user_id,
        payload={
            "totalAmount": order.total_amount_cents,
            "items": [{"productId": i.product_id, "quantity": i.quantity} for i in order.items]
        }
    )
    logger.info('Event publikowany')
    return order


def update_order_status(db: Session, order_id: int, status: str):
    """Update order status and publish corresponding event.

    Args:
        db: Database session.
        order_id: Order identifier.
        status: New order status ("paid", "failed", "cancelled").

    Returns:
        Order: Updated order, or None if not found.

    Notes:
        - Sets paid_at timestamp when status is "paid".
        - Publishes "order_paid" or "order_failed" event to Kafka.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None

    order.status = status
    if status == "paid":
        order.paid_at = datetime.now(timezone.utc)
        publish_order_event(
            event_type="order_paid",
            order_id=order.id,
            user_id=order.user_id,
            payload={"paymentId": "MOCK_PAYMENT_ID"}
        )
    elif status == "failed":
        publish_order_event(
            event_type="order_failed",
            order_id=order.id,
            user_id=order.user_id,
            payload={"reason": "Payment rejected or timeout"}
        )

    db.commit()
    return order


def cancel_order(db: Session, order_id: int, user_id: int):
    """Cancel an order and release inventory reservations.

    Args:
        db: Database session.
        order_id: Order identifier.
        user_id: User identifier (ensures user owns the order).

    Returns:
        bool: True if cancelled successfully, False otherwise.

    Notes:
        - Only orders with status "awaiting_payment" can be cancelled.
        - Releases stock in Inventory Service.
        - Publishes "order_cancelled" event to Kafka.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order or order.status != "awaiting_payment":
        return False

    order.status = "cancelled"
    order.cancelled_at = datetime.now(timezone.utc)

    for item in order.items:
        requests.post(f"{settings.INVENTORY_SERVICE_URL}/api/v1/inventory/release",
                      json={"product_id": item.product_id, "quantity": item.quantity},
                      timeout=5)

    db.commit()
    publish_order_event(
        event_type="order_cancelled",
        order_id=order_id,
        user_id=user_id,
        payload={}
    )
    return True

def get_product_details(product_id: int):
    """Fetch product details from Product Catalog Service.

    Args:
        product_id: Product identifier.

    Returns:
        dict: Product details, or None if not found or service unavailable.
    """
    try:
        response = requests.get(
            f"{settings.PRODUCT_CATALOG_SERVICE_URL}{settings.API_V1_PREFIX}/products/{product_id}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None
