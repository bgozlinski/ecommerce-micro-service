from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route



router = APIRouter()

@route(
    request_method=router.post,
    path="/login",
    status_code=200,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=False,

)
async def login(request: Request, response: Response):
    pass

@route(
    request_method=router.post,
    path="/register",
    status_code=201,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=False,
)
async def register(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/users",
    status_code=200,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=True,
)
async def list_users(request: Request, response: Response):
    pass