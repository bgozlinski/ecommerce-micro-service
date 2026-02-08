"""Order management API endpoints.

This module defines REST API routes for shopping cart operations, order
creation (checkout), order retrieval, cancellation, and key delivery.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import order as order_crud
from app.schemas.order import OrderOut, CartItemOut, CartAdd
from app.core.config import settings
from app.models.order import Order
from app.kafka import publish_order_event
import requests
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/orders", tags=["orders"])

@router.post("/cart", response_model=CartItemOut)
def add_to_cart(payload: CartAdd, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    """Add a product to the user's shopping cart.

    Args:
        payload: Product ID and quantity to add.
        x_user_id: User ID from gateway header.
        db: Database session dependency.

    Returns:
        CartItemOut: Updated cart item with total quantity.
    """
    return order_crud.add_to_cart(db, x_user_id, payload.product_id, payload.quantity)


@router.post("/checkout", response_model=OrderOut)
def checkout(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    """Create an order from the user's cart.

    This endpoint converts cart items into an order, reserves stock in the
    Inventory Service, and publishes an "order_created" event. The cart is
    cleared upon successful order creation.

    Args:
        x_user_id: User ID from gateway header.
        db: Database session dependency.

    Returns:
        OrderOut: Created order with status "awaiting_payment".

    Raises:
        HTTPException: 400 if cart is empty or stock unavailable.
    """
    order = order_crud.create_order_from_cart(db, x_user_id)
    if not order:
        raise HTTPException(status_code=400, detail="Checkout failed (stock unavailable or empty cart)")
    return order


@router.get("/my", response_model=list[OrderOut])
def get_my_orders(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    """Retrieve all orders for the authenticated user.

    Args:
        x_user_id: User ID from gateway header.
        db: Database session dependency.

    Returns:
        list[OrderOut]: List of user's orders.
    """
    return db.query(Order).filter(Order.user_id == x_user_id).all()

@router.get("/internal/{order_id}", response_model=OrderOut)
def get_order_for_internal_services(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/{order_id}", response_model=OrderOut)
def get_order_details(order_id: int, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    """Retrieve order details for a specific order.

    Args:
        order_id: Order identifier.
        x_user_id: User ID from gateway header (ensures user owns the order).
        db: Database session dependency.

    Returns:
        OrderOut: Order details including items.

    Raises:
        HTTPException: 404 if order not found or doesn't belong to user.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == x_user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    """Cancel an order and release reserved stock.

    Only orders with status "awaiting_payment" can be cancelled. Releases
    inventory reservations and publishes "order_cancelled" event.

    Args:
        order_id: Order identifier.
        x_user_id: User ID from gateway header.
        db: Database session dependency.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: 400 if order cannot be cancelled.
    """
    success = order_crud.cancel_order(db, order_id, x_user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel order")
    return {"message": "Order cancelled"}


@router.get("/{order_id}/keys")
def get_order_keys(order_id: int, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    """Retrieve game keys for a paid order.

    Fetches license keys from the Inventory Service for all items in the order.
    Keys are only available for orders with status "paid".

    Args:
        order_id: Order identifier.
        x_user_id: User ID from gateway header.
        db: Database session dependency.

    Returns:
        dict: Dictionary containing list of game keys.

    Raises:
        HTTPException: 404 if order not found.
        HTTPException: 403 if order is not paid.
        HTTPException: 503 if Inventory Service is unavailable.
        HTTPException: 500 if key retrieval fails.
    """
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == x_user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != "paid":
        raise HTTPException(status_code=403, detail="Keys available only for paid orders")

    order_item_ids = [item.id for item in order.items]

    try:
        response = requests.post(
            f"{settings.INVENTORY_SERVICE_URL}/api/v1/inventory/get-keys",
            json=order_item_ids,
            timeout=5
        )
        if response.status_code == 200:
            return {"keys": response.json()}

        raise HTTPException(status_code=500, detail="Failed to fetch keys from inventory service")
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Inventory service unavailable")


@router.post("/{order_id}/payment-status")
def update_payment_status(
        order_id: int,
        status: str,
        payment_id: str = None,
        db: Session = Depends(get_db)
):
    """Update order status after payment completion.

    This endpoint is called by the Payment Service (not through API Gateway)
    after receiving a Stripe webhook. It updates the order status and either
    confirms or releases inventory reservations based on payment outcome.

    Args:
        order_id: Order identifier.
        status: Payment status ("success" or "failed").
        payment_id: Stripe payment ID. Optional.
        db: Database session dependency.

    Returns:
        dict: Success message with order_id.

    Raises:
        HTTPException: 404 if order not found.
        HTTPException: 400 if status is invalid.

    Notes:
        - Does NOT require X-User-Id header (service-to-service call).
        - Publishes "order_paid" or "order_failed" event to Kafka.
    """

    if status == "success":
        order = order_crud.update_order_status(db, order_id, "paid")
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        for item in order.items:
            try:
                requests.post(
                    f"{settings.INVENTORY_SERVICE_URL}/api/v1/inventory/confirm",
                    json={"product_id": item.product_id, "quantity": item.quantity},
                    timeout=5
                )
            except requests.RequestException:
                logger.error(f"Failed to confirm reservation for product {item.product_id}")

        return {"message": "Order marked as paid", "order_id": order_id}

    elif status == "failed":
        order = order_crud.update_order_status(db, order_id, "failed")
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        for item in order.items:
            try:
                requests.post(
                    f"{settings.INVENTORY_SERVICE_URL}/api/v1/inventory/release",
                    json={"product_id": item.product_id, "quantity": item.quantity},
                    timeout=5
                )
            except requests.RequestException:
                logger.error(f"Failed to release reservation for product {item.product_id}")

        return {"message": "Order marked as failed", "order_id": order_id}

    else:
        raise HTTPException(status_code=400, detail="Invalid status")


