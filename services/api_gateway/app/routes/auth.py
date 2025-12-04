from fastapi import APIRouter, Depends, HTTPException, status
import httpx
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)


USER_SERVICE_URL = 'http://auth-service:8000/api/v1/users'


@router.get("/users")
async def get_users():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(USER_SERVICE_URL, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
