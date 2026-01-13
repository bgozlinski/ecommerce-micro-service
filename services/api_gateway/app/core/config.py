"""Configuration for the API Gateway service.

This module defines the `Settings` class, which uses `pydantic-settings`
(`BaseSettings`) to read configuration from environment variables and a `.env`
file. It centralizes URLs for internal services and security parameters
(JWT settings, timeouts, etc.).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        JWT_SECRET_KEY: Secret used to sign/verify JWTs.
        JWT_ALGORITHM: JWT signing algorithm. Defaults to `HS256`.
        ACCESS_TOKEN_EXPIRE_MINUTES: Access-token TTL in minutes. Defaults to 1440 (24h).
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh-token TTL in days. Defaults to 7.

        PROJECT_NAME: Human-friendly application name for docs/metadata.
        API_V1_PREFIX: Base prefix for public API routes (e.g., `/api/v1`).
        ENVIRONMENT: Deployment environment label (e.g., `development`, `production`).
        DEBUG: Enables additional debug features/logging in dev environments.

        AUTH_SERVICE_URL: Base URL for the Auth Service inside the network
            (e.g., `http://auth-service:8000`).
    """

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PROJECT_NAME: str = "API Gateway"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    PRODUCT_SERVICE_URL: str = "http://product-service:8000"
    ORDER_SERVICE_URL: str = "http://order-service:8000"
    INVENTORY_SERVICE_URL: str = "http://inventory-service:8000"


    class Config:
        """Settings source configuration.

        Reads variables from `.env` and treats names as case-sensitive.
        """

        env_file = ".env"
        case_sensitive = True

settings = Settings()
