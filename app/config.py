from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillTrack"
    DATABASE_URL: str = "sqlite:///./skilltrack.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
