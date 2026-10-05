from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./kanban.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
