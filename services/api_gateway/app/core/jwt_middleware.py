from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.config import settings
from app.core.security import decode_access_token

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, public_paths: list[str] | None = None):
        super().__init__(app)
        self.public_paths = set(public_paths or [])

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in self.public_paths:
            return await call_next(request)

        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized", "message": "Missing Bearer token", "statusCode": 401}, status_code=401)

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = decode_access_token(token)
            request.state.user = {
                "user_id": payload.get("sub") or payload.get("user_id"),
                "role": payload.get("role") or payload.get("X-User-Role"),
                "raw": payload,
            }
        except ExpiredSignatureError:
            return JSONResponse({"error": "Unauthorized", "message": "Token expired", "statusCode": 401}, status_code=401)
        except InvalidTokenError:
            return JSONResponse({"error": "Unauthorized", "message": "Invalid token", "statusCode": 401}, status_code=401)

        return await call_next(request)
