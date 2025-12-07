from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PROJECT_NAME: str = "API Gateway"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    AUTH_SERVICE_URL: str = "http://auth-service:8000"


    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
