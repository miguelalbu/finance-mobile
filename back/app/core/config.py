from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/finance"
    SECRET_KEY: str = "changeme-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    BRAPI_BASE_URL: str = "https://brapi.dev/api"
    BRAPI_TOKEN: str = ""

    SCHEDULER_INTERVAL_MINUTES: int = 30
    TESTING: bool = False


settings = Settings()
