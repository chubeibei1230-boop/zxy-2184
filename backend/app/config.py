from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    DATABASE_URL: str = "sqlite:///./wax_mold.db"

    API_V1_PREFIX: str = "/api"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8121


settings = Settings()
