from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PulseEngine"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/pulse_db"
    REDIS_URL: str = "redis://redis:6379/0"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()