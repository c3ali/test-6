from pydantic_settings import BaseSettings
from pydantic import Field
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost/trello_clone"
    JWT_SECRET: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REDIS_URL: str = "redis://localhost:6379"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    API_V1_PREFIX: str = "/api/v1"
    WEBSOCKET_PREFIX: str = "/ws"
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
settings = Settings()