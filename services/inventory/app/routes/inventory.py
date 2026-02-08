"""Inventory management API endpoints.

This module defines REST API routes for stock management, including
reservations, confirmations, releases, and key management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories import inventory as inventory_crud
from app.schemas.inventory import InventoryOut, ReserveRequest, ConfirmRequest, KeyCreate
from app.core.config import settings
from typing import List

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/inventory", tags=["inventory"])

@router.get("/{product_id}", response_model=InventoryOut)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    """Retrieve inventory status for a product.

    Args:
        product_id: Product identifier.
        db: Database session dependency.

    Returns:
        InventoryOut: Inventory record with available and reserved quantities.

    Raises:
        HTTPException: 404 if inventory record not found.
    """
    inventory = inventory_crud.get_inventory_by_product_id(db, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return inventory

@router.post("/reserve", status_code=status.HTTP_200_OK)
def reserve_stock(payload: ReserveRequest, db: Session = Depends(get_db)):
    """Reserve stock for an order.

    Decreases available quantity and increases reserved quantity. Ensures
    sufficient keys are available before reserving.

    Args:
        payload: Product ID and quantity to reserve.
        db: Database session dependency.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: 400 if insufficient stock or keys available.
    """
    success = inventory_crud.reserve_stock(db, payload.product_id, payload.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient stock or keys available")
    return {"message": "Stock reserved successfully"}

@router.post("/confirm", status_code=status.HTTP_200_OK)
def confirm_stock(payload: ConfirmRequest, db: Session = Depends(get_db)):
    """Confirm reservation and assign keys to order items.

    Decreases reserved quantity, assigns available keys to order items,
    and returns the assigned keys.

    Args:
        payload: Product ID, quantity, and order item IDs.
        db: Database session dependency.

    Returns:
        dict: Success message and list of assigned keys.

    Raises:
        HTTPException: 400 if confirmation fails.
    """
    keys = inventory_crud.confirm_reservation(db, payload.product_id, payload.quantity, payload.order_item_ids)
    if not keys:
        raise HTTPException(status_code=400, detail="Failed to confirm reservation")
    return {"message": "Reservation confirmed", "keys": keys}

@router.post("/release", status_code=status.HTTP_200_OK)
def release_stock(payload: ReserveRequest, db: Session = Depends(get_db)):
    """Release a reservation and return stock to available.

    Increases available quantity and decreases reserved quantity. Called
    when an order is cancelled or payment fails.

    Args:
        payload: Product ID and quantity to release.
        db: Database session dependency.

    Returns:
        dict: Success message.

    Raises:
        HTTPException: 400 if release fails.
    """
    success = inventory_crud.release_stock(db, payload.product_id, payload.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to release reservation")
    return {"message": "Stock released successfully"}

@router.post("/keys", status_code=status.HTTP_201_CREATED)
def add_keys(payload: KeyCreate, db: Session = Depends(get_db)):
    """Add license keys to a product's inventory.

    Args:
        payload: Product ID and list of key values.
        db: Database session dependency.

    Returns:
        dict: Success message and count of added keys.

    Raises:
        HTTPException: 400 if keys already exist.
    """
    inventory, added_count = inventory_crud.add_keys(db, payload.product_id, payload.keys)

    if added_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="key already added"
        )

    return {"message": "Keys added successfully", "added_count": added_count}

@router.post("/get-keys", response_model=List[str])
def get_keys(order_item_ids: List[int], db: Session = Depends(get_db)):
    """Retrieve assigned keys for order items.

    Args:
        order_item_ids: List of order item identifiers.
        db: Database session dependency.

    Returns:
        List[str]: List of key values assigned to the order items.
    """
    return inventory_crud.get_keys_by_order_items(db, order_item_ids)
