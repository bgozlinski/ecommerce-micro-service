from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
import httpx
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)


# USER_SERVICE_URL = 'http://auth-service:8000/api/v1/users'

async def auth_proxy(request: Request, path: str):
    target = f"{settings.AUTH_SERVICE_URL}{settings.API_V1_PREFIX}{path}"
    body = await request.body()

    forward_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("content-length", "host",  "connection")
    }

    user = getattr(request.state, "user", None)
    if user and user.get("user_id"):
        forward_headers["X-User-Id"] = str(user["user_id"])
    if user and user.get("role"):
        forward_headers["X-User-Role"] = str(user["role"])

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            request.method, target,
            content=body,
            headers=forward_headers,
            params=request.query_params,
            timeout=15.0,
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=dict(resp.headers),
        media_type=resp.headers.get("content-type"),
    )

@router.get("/users")
async def get_users(request: Request):
    return await auth_proxy(request, "/users")

@router.post("/register")
async def register(request: Request):
    return await auth_proxy(request, "/register")

@router.post("/login")
async def login(request: Request):
    return await auth_proxy(request, "/login")


# @router.get("/users")
# async def get_users():
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.get(USER_SERVICE_URL, timeout=10.0)
#             response.raise_for_status()
#             return response.json()
#         except httpx.HTTPError as e:
#             raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
