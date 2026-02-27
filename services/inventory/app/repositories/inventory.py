"""Repository layer for inventory management database operations.

This module provides functions for managing stock levels and digital license keys.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.inventory import Inventory, ProductKeys
from datetime import datetime, timezone

def get_inventory_by_product_id(db: Session, product_id: int) -> Optional[Inventory]:
    """Retrieve inventory summary for a given product.

    Args:
        db: Database session.
        product_id: ID of the product.

    Returns:
        Optional[Inventory]: Inventory summary or None if not found.
    """
    return db.query(Inventory).filter(and_(Inventory.product_id == product_id)).first()

def add_keys(db: Session, product_id: int, keys: List[str]) -> tuple[Optional[Inventory], int]:
    """Batch add digital license keys for a product and update stock.

    Args:
        db: Database session.
        product_id: ID of the product.
        keys: List of unique key strings to add.

    Returns:
        tuple: (updated_inventory_record, count_of_added_keys).
    """
    existing_keys = db.query(ProductKeys).filter(
        ProductKeys.key_value.in_(keys)
    ).all()
    existing_key_values = {k.key_value for k in existing_keys}

    new_keys = [k for k in keys if k not in existing_key_values]

    if not new_keys:
        return get_inventory_by_product_id(db, product_id), 0

    for val in new_keys:
        db_key = ProductKeys(product_id=product_id, key_value=val, status="available")
        db.add(db_key)

    inventory = get_inventory_by_product_id(db, product_id)
    if not inventory:
        inventory = Inventory(product_id=product_id, available_qty=len(new_keys), reserved_qty=0)
        db.add(inventory)
    else:
        inventory.available_qty += len(new_keys)
        inventory.updated_at = datetime.now(timezone.utc)

    db.commit()
    return inventory, len(new_keys)

def reserve_stock(db: Session, product_id: int, quantity: int) -> bool:
    """Reserve digital license keys for a pending order.

    Args:
        db: Database session.
        product_id: ID of the product.
        quantity: Number of keys to reserve.

    Returns:
        bool: True if reservation succeeded, False otherwise.
    """
    inventory = get_inventory_by_product_id(db, product_id)
    if not inventory or inventory.available_qty < quantity:
        return False

    inventory.available_qty -= quantity
    inventory.reserved_qty += quantity
    inventory.updated_at = datetime.now(timezone.utc)

    keys = db.query(ProductKeys).filter(
        and_(ProductKeys.product_id == product_id, ProductKeys.status == "available")
    ).limit(quantity).with_for_update().all()

    if len(keys) < quantity:
        db.rollback()
        return False

    for key in keys:
        key.status = "reserved"
        key.updated_at = datetime.now(timezone.utc)

    db.commit()
    return True

def release_stock(db: Session, product_id: int, quantity: int) -> bool:
    """Release a previously made stock reservation.

    Args:
        db: Database session.
        product_id: ID of the product.
        quantity: Number of keys to release back to 'available' status.

    Returns:
        bool: True if release succeeded, False otherwise.
    """
    inventory = get_inventory_by_product_id(db, product_id)
    if not inventory or inventory.reserved_qty < quantity:
        return False

    inventory.available_qty += quantity
    inventory.reserved_qty -= quantity
    inventory.updated_at = datetime.now(timezone.utc)

    keys = db.query(ProductKeys).filter(
        and_(ProductKeys.product_id == product_id, ProductKeys.status == "reserved")
    ).limit(quantity).with_for_update().all()

    for key in keys:
        key.status = "available"
        key.updated_at = datetime.now(timezone.utc)

    db.commit()
    return True

def confirm_reservation(db: Session, product_id: int, quantity: int, order_item_ids: List[int]) -> List[str]:
    """Confirm a stock reservation by assigning keys to specific order items.

    Args:
        db: Database session.
        product_id: ID of the product.
        quantity: Number of keys to confirm.
        order_item_ids: IDs of order items to assign keys to.

    Returns:
        List[str]: List of key values confirmed and assigned.
    """
    inventory = get_inventory_by_product_id(db, product_id)
    if not inventory or inventory.reserved_qty < quantity:
        return []

    inventory.reserved_qty -= quantity
    inventory.updated_at = datetime.now(timezone.utc)

    keys = db.query(ProductKeys).filter(
        and_(ProductKeys.product_id == product_id, ProductKeys.status == "reserved")
    ).limit(quantity).with_for_update().all()

    assigned_keys = []
    for i, key in enumerate(keys):
        key.status = "assigned"
        if i < len(order_item_ids):
            key.order_item_id = order_item_ids[i]
        key.updated_at = datetime.now(timezone.utc)
        assigned_keys.append(key.key_value)

    db.commit()
    return assigned_keys

def get_keys_by_order_items(db: Session, order_item_ids: List[int]) -> List[str]:
    """Retrieve all keys currently assigned to a set of order items.

    Args:
        db: Database session.
        order_item_ids: List of order item IDs.

    Returns:
        List[str]: List of license key values.
    """
    keys = db.query(ProductKeys).filter(
        ProductKeys.order_item_id.in_(order_item_ids)
    ).all()
    return [k.key_value for k in keys]
