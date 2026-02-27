from fastapi import APIRouter, Request, Response
from app.core.config import settings
from app.core.route_wrapper import route

router = APIRouter()

@route(
    request_method=router.get,
    path="/reports/daily",
    status_code=200,
    service_url=settings.REPORTING_SERVICE_URL,
    authentication_required=True,
    admin_required=True
)
async def get_daily_reports(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/reports/monthly",
    status_code=200,
    service_url=settings.REPORTING_SERVICE_URL,
    authentication_required=True,
    admin_required=True
)
async def get_monthly_reports(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/reports/top-products",
    status_code=200,
    service_url=settings.REPORTING_SERVICE_URL,
    authentication_required=True,
    admin_required=True
)
async def get_top_products(request: Request, response: Response):
    pass

@route(
    request_method=router.get,
    path="/reports/export/daily",
    status_code=200,
    service_url=settings.REPORTING_SERVICE_URL,
    authentication_required=True,
    admin_required=True
)
async def export_daily_reports(request: Request, response: Response):
    pass
