"""Configuration settings for the Auth Service.

This module defines the Settings class which loads configuration from
environment variables and .env file. It includes database credentials,
JWT settings for authentication, and general application configuration.
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
        
        JWT_SECRET_KEY: Secret key used to sign and verify JWT tokens.
        JWT_ALGORITHM: JWT signing algorithm. Defaults to "HS256".
        ACCESS_TOKEN_EXPIRE_MINUTES: Access token TTL in minutes. Defaults to 1440 (24h).
        REFRESH_TOKEN_EXPIRE_DAYS: Refresh token TTL in days. Defaults to 7.
        
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

    JWT_SECRET_KEY: str = "test_secret_key_for_development_only_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PROJECT_NAME: str = "Auth Service"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_TOPIC_USERS: str = "users"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL.
        
        Returns:
            str: Full database connection string.
        """
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
