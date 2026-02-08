"""Configuration settings for the Product Catalog Service.

This module defines the Settings class which loads configuration from
environment variables and .env file. It includes database credentials
and general application configuration.
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
    """
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str = "5432"
    DB_NAME: str

    PROJECT_NAME: str = "Product Service"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL.
        
        Returns:
            str: Full database connection string.
        """
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
