"""Product Catalog proxy routes for the API Gateway.

These endpoints forward requests to the Product Catalog Service using the custom
`route` wrapper. For protected routes, the gateway verifies the client JWT and
injects `X-User-Id` and `X-User-Role` headers into the internal request. Downstream
services trust these headers and do not verify JWTs again (per project guidelines).

Access model:
- GET /products, GET /products/{product_id}: public (no auth)
- POST /products, PATCH /products/{product_id}, DELETE /products/{product_id}: admin-only
"""

from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.get,
    path="/products",
    status_code=200,
    service_url=settings.PRODUCT_SERVICE_URL,
    authentication_required=False,

)
async def list_products(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/products/{product_id}",
    status_code=200,
    service_url=settings.PRODUCT_SERVICE_URL,
    authentication_required=False,

)
async def read_product(request: Request, response: Response):
    pass

@route(
    request_method=router.post,
    path="/products",
    status_code=201,
    service_url=settings.PRODUCT_SERVICE_URL,
    authentication_required=True,
    admin_required=True
)
async def create_product(request: Request, response: Response):
    pass

@route(
    request_method=router.patch,
    path="/products/{product_id}",
    status_code=200,
    service_url=settings.PRODUCT_SERVICE_URL,
    authentication_required=True,
    admin_required=True,
)
async def update_product(request: Request, response: Response):
    pass

@route(
    request_method=router.delete,
    path="/products/{product_id}",
    status_code=204,
    service_url=settings.PRODUCT_SERVICE_URL,
    authentication_required=True,
    admin_required=True,
)
async def delete_product(request: Request, response: Response):
    pass
