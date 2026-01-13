from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.post,
    path="/orders/cart",
    status_code=201,
    service_url=settings.ORDER_SERVICE_URL,
    authentication_required=True
)
async def add_to_cart(request: Request, response: Response):
    pass

@route(
    request_method=router.post,
    path="/orders/checkout",
    status_code=201,
    service_url=settings.ORDER_SERVICE_URL,
    authentication_required=True
)
async def checkout(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/orders/my",
    status_code=200,
    service_url=settings.ORDER_SERVICE_URL,
    authentication_required=True
)
async def get_my_orders(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/orders/{order_id}",
    status_code=200,
    service_url=settings.ORDER_SERVICE_URL,
    authentication_required=True,
)
async def get_order_details(request: Request, response: Response):
    pass

@route(
    request_method=router.post,
    path="/orders/{order_id}/cancel",
    status_code=200,
    service_url=settings.ORDER_SERVICE_URL,
    authentication_required=True
)
async def cancel_order(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/orders/{order_id}/keys",
    status_code=200,
    service_url=settings.ORDER_SERVICE_URL,
    authentication_required=True
)
async def get_order_keys(request: Request, response: Response):
    pass