from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.post,
    path="/payments/create",
    status_code=201,
    service_url=settings.PAYMENT_SERVICE_URL,
    authentication_required=True
)
async def create_payment(request: Request, response: Response):
    pass

@route(
    request_method=router.post,
    path="/payments/webhook",
    status_code=200,
    service_url=settings.PAYMENT_SERVICE_URL,
    authentication_required=False
)
async def payment_webhook(request: Request, response: Response):
    pass