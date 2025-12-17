"""Auth-related proxy routes for the API Gateway.

These endpoints forward requests to the Auth Service using the custom `route`
wrapper. For protected routes, the gateway verifies the client JWT and injects
`X-User-Id` and `X-User-Role` headers into the internal request. Downstream
services trust these headers and do not verify JWTs again (per project guidelines).

Access model:
- POST /register: public
- GET /users, GET /users/{user_id}, DELETE /users/{user_id}, PATCH /users/{user_id}:
  admin-only (enforced at gateway via `admin_required=True`)
"""

from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

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

@route(
    request_method=router.get,
    path="/users/{user_id}",
    status_code=200,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=True,
)
async def get_user_by_id(request: Request, response: Response):
    pass

@route(
    request_method=router.delete,
    path="/users/{user_id}",
    status_code=200,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=True,
)
async def delete_user(request: Request, response: Response):
    pass

@route(
    request_method=router.patch,
    path="/users/{user_id}",
    status_code=200,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=True,
    admin_required=True,
)
async def patch_user(request: Request, response: Response):
    pass