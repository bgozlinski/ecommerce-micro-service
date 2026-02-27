"""Configuration settings for the Payment Service.

This module defines the Settings class which loads configuration from
environment variables and .env file. It includes database credentials,
Stripe API keys, and URLs for inter-service communication.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        DB_USER: Database username.
        DB_PASSWORD: Database password.
        DB_HOST: Database host address.
        DB_PORT: Database port. Defaults to "5432".
        DB_NAME: Database name.

        PROJECT_NAME: Human-friendly service name.
        API_V1_PREFIX: Base prefix for API routes (e.g., "/api/v1").
        ENVIRONMENT: Deployment environment (e.g., "development", "production").
        DEBUG: Enable debug mode for development.

        STRIPE_SECRET_KEY: Stripe secret API key for server-side operations.
        STRIPE_PUBLISHABLE_KEY: Stripe publishable key for client-side.
        STRIPE_WEBHOOK_SECRET: Secret for verifying Stripe webhook signatures.

        ORDER_SERVICE_URL: Base URL for Order Service internal communication.
        FRONTEND_URL: Frontend application URL for redirect URLs.
    """

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str = "5432"
    DB_NAME: str

    PROJECT_NAME: str = "Payment Service"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    ORDER_SERVICE_URL: str = "http://order-service:8000"
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL.

        Returns:
            str: Full database connection string.
        """
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
