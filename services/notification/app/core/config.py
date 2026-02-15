from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
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
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str = "noreply@gamekeys.com"
    SMTP_FROM_NAME: str = "GameKeys Store"

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    DISCORD_WEBHOOK_URL: str = ""


settings = Settings()