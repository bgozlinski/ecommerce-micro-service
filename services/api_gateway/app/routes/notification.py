from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.get,
    path="/notifications/channels",
    status_code=200,
    service_url=settings.NOTIFICATION_SERVICE_URL,
    authentication_required=True
)
async def get_channels(request: Request, response: Response):
    pass

@route(
    request_method=router.post,
    path="/notifications/channels",
    status_code=201,
    service_url=settings.NOTIFICATION_SERVICE_URL,
    authentication_required=True
)
async def add_channel(request: Request, response: Response):
    pass

@route(
    request_method=router.patch,
    path="/notifications/channels/{channel_id}",
    status_code=200,
    service_url=settings.NOTIFICATION_SERVICE_URL,
    authentication_required=True
)
async def update_channel_settings(request: Request, response: Response):
    pass

@route(
    request_method=router.delete,
    path="/notifications/channels/{channel_id}",
    status_code=204,
    service_url=settings.NOTIFICATION_SERVICE_URL,
    authentication_required=True
)
async def remove_channel(request: Request, response: Response):
    pass
