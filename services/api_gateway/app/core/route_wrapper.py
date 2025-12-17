from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.security import decode_access_token
import httpx
import functools


def generate_request_headers(payload: dict) -> dict:
    """Build gateway context headers from a decoded JWT payload.

    Extracts the user identifier and role from common JWT claim names and
    returns a header dictionary that downstream services in this project rely on.

    Header mapping:
      - ``X-User-Id`` from ``sub`` or ``user_id`` claim
      - ``X-User-Role`` from ``role`` or ``X-User-Role`` claim

    Notes:
      - Services trust these headers (the gateway verifies JWTs). See project
        guidelines: Services must not verify JWTs themselves.

    Args:
      payload: The decoded JWT payload (dict of claims).

    Returns:
      dict: Headers to forward to internal services (possibly empty).
    """
    headers = {}
    user_id = payload.get("sub") or payload.get("user_id")
    role = payload.get("role") or payload.get("X-User-Role")
    if user_id:
        headers["X-User-Id"] = str(user_id)
    if role:
        headers["X-User-Role"] = str(role)
    return headers


def import_function(method_path: str):
    """Dynamically import a function by its dotted path.

    Example:
      ``import_function("pkg.module.my_hook")`` -> returns ``my_hook`` or ``None``.

    Args:
      method_path: Dotted path to the target callable (e.g., "a.b.c").

    Returns:
      The attribute referenced by the last segment of the path if found,
      otherwise ``None``.
    """
    module, method = method_path.rsplit('.', 1)
    mod = __import__(module, fromlist=[method])
    return getattr(mod, method, None)


def route(request_method,
          path: str,
          status_code: int,
          service_url: str,
          authentication_required: bool = False,
          post_processing_func: Optional[str] = None,
          timeout_seconds: float = 15.0,
          admin_required: bool = False
          ) -> Callable:
    """Decorator factory to register a proxy route to an internal service.

    This helper attaches a FastAPI route (via the provided ``request_method``
    such as ``app.get``/``app.post``) that forwards the incoming request to a
    downstream service URL while handling:
      - Optional JWT verification at the gateway level.
      - Propagation of user context headers (``X-User-Id``, ``X-User-Role``).
      - Transparent streaming of status code and response content-type.
      - Optional post-processing hook on successful responses.

    The resulting decorator should wrap a no-op handler (the wrapped function
    isn't called; it exists only to satisfy FastAPI's signature requirements).

    Args:
      request_method: A FastAPI route registrar like `app.get` or `app.post`.
      path: The path to bind on the gateway (e.g., "/api/v1/users").
      status_code: Expected success status; if matched, the post hook is invoked.
      service_url: Base URL of the internal service (e.g., settings.AUTH_SERVICE_URL).
      authentication_required: When True, validates the Authorization Bearer token
        and derives user context headers.
      post_processing_func: Optional dotted path to a callable hook that accepts
        raw `bytes` response content and returns transformed content.
      timeout_seconds: HTTP client timeout for the upstream request.
      admin_required: When True, the gateway requires a valid JWT and enforces that
        the user role is `admin`. Missing/invalid token yields 401; non-admin role yields 403.

    Returns:
      Callable: A decorator that registers the proxy route.
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

            if admin_required:
                role = (payload.get("role") or payload.get("X-User-Role") or "").lower()
                if role != "admin":
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this resource")

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
