"""Auth-related proxy routes for the API Gateway.

These endpoints forward requests to the Auth Service using the custom `route`
wrapper. For protected routes, the wrapper decodes the client JWT at the
gateway and injects `X-User-Id` and `X-User-Role` headers into the internal
request. The downstream services trust these headers and do not verify the JWT
again (per project guidelines).
"""

from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.post,
    path="/login",
    status_code=200,
    service_url=settings.AUTH_SERVICE_URL,
    authentication_required=True,

)
async def login(request: Request, response: Response):
    pass
