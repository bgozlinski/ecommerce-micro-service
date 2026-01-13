from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.post,
    path="/inventory/keys",
    status_code=201,
    service_url=settings.INVENTORY_SERVICE_URL,
    authentication_required=True,
    admin_required=True
)
async def add_keys(request: Request, response: Response):
    pass