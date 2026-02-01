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

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/orders", tags=["orders"])

@router.post("/cart", response_model=CartItemOut)
def add_to_cart(payload: CartAdd, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    return order_crud.add_to_cart(db, x_user_id, payload.product_id, payload.quantity)


@router.post("/checkout", response_model=OrderOut)
def checkout(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    order = order_crud.create_order_from_cart(db, x_user_id)
    if not order:
        raise HTTPException(status_code=400, detail="Checkout failed (stock unavailable or empty cart)")
    return order


@router.get("/my", response_model=list[OrderOut])
def get_my_orders(x_user_id: int = Header(...), db: Session = Depends(get_db)):
    # logger.info(f"Getting orders for user {x_user_id}")
    # publish_order_event(
    #     event_type="order_created",
    #     order_id='3123123',
    #     user_id='1',
    #     payload={
    #         "totalAmount": '10_000',
    #         "items": ['1', '2']
    #     }
    # )
    return db.query(Order).filter(Order.user_id == x_user_id).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order_details(order_id: int, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == x_user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, x_user_id: int = Header(...), db: Session = Depends(get_db)):
    success = order_crud.cancel_order(db, order_id, x_user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel order")
    return {"message": "Order cancelled"}


@router.get("/{order_id}/keys")
def get_order_keys(order_id: int, x_user_id: int = Header(...), db: Session = Depends(get_db)):
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