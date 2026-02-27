"""Configuration settings for the reporting service.

This module defines all configuration parameters loaded from environment variables,
including database connection and Kafka settings.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        DB_USER: Database username.
        DB_PASSWORD: Database password.
        DB_HOST: Database host address.
        DB_PORT: Database port (default: 5432).
        DB_NAME: Database name.
        ENVIRONMENT: Application environment (development/production).
        DEBUG: Debug mode flag.
        API_V1_PREFIX: API version prefix for routes.
        PROJECT_NAME: Project display name.
        KAFKA_BOOTSTRAP_SERVERS: Kafka broker addresses.
        KAFKA_GROUP_ID: Consumer group identifier.
        KAFKA_TOPIC_ORDERS: Orders topic name.
        KAFKA_TOPIC_PRODUCTS: Products topic name.
    """
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str = "5432"
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Reporting Service"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_GROUP_ID: str = "reporting-service-group"
    KAFKA_TOPIC_ORDERS: str = "orders"
    KAFKA_TOPIC_PRODUCTS: str = "products"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
