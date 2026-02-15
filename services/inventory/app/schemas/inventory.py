from pydantic import BaseModel
from typing import List
from datetime import datetime

class InventoryOut(BaseModel):
    id: int
    product_id: int
    available_qty: int
    reserved_qty: int
    updated_at: datetime

    class Config:
        from_attributes = True

class ReserveRequest(BaseModel):
    product_id: int
    quantity: int

class ConfirmRequest(BaseModel):
    product_id: int
    quantity: int
    order_item_ids: List[int]

class KeyCreate(BaseModel):
    product_id: int
    keys: List[str]