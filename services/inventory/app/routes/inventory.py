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
    inventory = inventory_crud.get_inventory_by_product_id(db, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return inventory

@router.post("/reserve", status_code=status.HTTP_200_OK)
def reserve_stock(payload: ReserveRequest, db: Session = Depends(get_db)):
    success = inventory_crud.reserve_stock(db, payload.product_id, payload.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient stock or keys available")
    return {"message": "Stock reserved successfully"}

@router.post("/confirm", status_code=status.HTTP_200_OK)
def confirm_stock(payload: ConfirmRequest, db: Session = Depends(get_db)):
    keys = inventory_crud.confirm_reservation(db, payload.product_id, payload.quantity, payload.order_item_ids)
    if not keys:
        raise HTTPException(status_code=400, detail="Failed to confirm reservation")
    return {"message": "Reservation confirmed", "keys": keys}

@router.post("/release", status_code=status.HTTP_200_OK)
def release_stock(payload: ReserveRequest, db: Session = Depends(get_db)):
    success = inventory_crud.release_stock(db, payload.product_id, payload.quantity)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to release reservation")
    return {"message": "Stock released successfully"}

@router.post("/keys", status_code=status.HTTP_201_CREATED)
def add_keys(payload: KeyCreate, db: Session = Depends(get_db)):
    inventory, added_count = inventory_crud.add_keys(db, payload.product_id, payload.keys)

    if added_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="key already added"
        )

    return {"message": "Keys added successfully", "added_count": added_count}

@router.post("/get-keys", response_model=List[str])
def get_keys(order_item_ids: List[int], db: Session = Depends(get_db)):
    return inventory_crud.get_keys_by_order_items(db, order_item_ids)
