# app/core/route_wrapper.py
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.security import decode_access_token
import httpx
import functools


def generate_request_headers(payload: dict) -> dict:
    headers = {}
    user_id = payload.get("sub") or payload.get("user_id")
    role = payload.get("role") or payload.get("X-User-Role")
    if user_id:
        headers["X-User-Id"] = str(user_id)
    if role:
        headers["X-User-Role"] = str(role)
    return headers


def import_function(method_path: str):
    module, method = method_path.rsplit('.', 1)
    mod = __import__(module, fromlist=[method])
    return getattr(mod, method, None)


def route(request_method,
          path: str,
          status_code: int,
          service_url: str,
          authentication_required: bool = False,
          post_processing_func: Optional[str] = None,
          timeout_seconds: float = 15.0):
    """Define a proxy endpoint that forwards to an internal service.
    - request_method: app.get/app.post/...
    - path: "/api/v1/users"
    - status_code: expected success status
    - service_url: e.g. settings.AUTH_SERVICE_URL
    - authentication_required: verify JWT if True
    - post_processing_func: optional callable path "pkg.mod.func(content|dict)"
    """
    app_any = request_method(path, status_code=status_code)

    def decorator(f: Callable):
        @app_any
        @functools.wraps(f)
        async def inner(request: Request, response: Response, **kwargs):
            payload = getattr(getattr(request, 'state', object()), 'user', {}).get('raw')
            if authentication_required and not payload:
                auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
                token = auth_header.split(" ", 1)[1].strip()
                try:
                    payload = decode_access_token(token)
                except ExpiredSignatureError:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
                except InvalidTokenError:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

            forward_headers = {
                k: v for k, v in request.headers.items()
                if k.lower() not in ("content-length", "host", "connection", "authorization", "transfer-encoding")
            }
            if payload:
                forward_headers.update(generate_request_headers(payload))

            url = f"{service_url}{request.url.path}"
            body = await request.body()
            try:
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    resp = await client.request(
                        request.method,
                        url,
                        content=body,
                        headers=forward_headers,
                        params=request.query_params,
                    )
            except httpx.RequestError:
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")

            content = resp.content
            if post_processing_func and resp.status_code == status_code:
                hook = import_function(post_processing_func)
                if callable(hook):
                    content = hook(content)

            response.status_code = resp.status_code
            return Response(content=content, media_type=resp.headers.get("content-type"))

        return inner

    return decorator
