"""Configuration settings for the notification service.

This module defines all configuration parameters loaded from environment variables,
including database connection, Kafka settings, SMTP configuration, and Discord webhook.
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
        KAFKA_TOPIC_USERS: Users topic name.
        KAFKA_TOPIC_PRODUCTS: Products topic name.
        SMTP_HOST: SMTP server host.
        SMTP_PORT: SMTP server port.
        SMTP_USER: SMTP username.
        SMTP_PASSWORD: SMTP password.
        SMTP_FROM_EMAIL: Default sender email address.
        SMTP_FROM_NAME: Default sender name.
        DISCORD_WEBHOOK_URL: Discord webhook URL for notifications.
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
    PROJECT_NAME: str = "Notification Service"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    KAFKA_GROUP_ID: str = "notification-service-group"
    KAFKA_TOPIC_ORDERS: str = "orders"
    KAFKA_TOPIC_USERS: str = "users"
    KAFKA_TOPIC_PRODUCTS: str = "products"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "test@example.com"
    SMTP_PASSWORD: str = "test_password"
    SMTP_FROM_EMAIL: str = "noreply@gamekeys.com"
    SMTP_FROM_NAME: str = "GameKeys Store"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    DISCORD_WEBHOOK_URL: str = ""


settings = Settings()