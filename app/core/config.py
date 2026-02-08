from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./reminder.db"
    TELEGRAM_BOT_TOKEN: str = ""
    SCHEDULER_SECRET: str = "supersecretkey"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

# Backwards-compatible module-level constants
DATABASE_URL = settings.DATABASE_URL
TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
SCHEDULER_SECRET = settings.SCHEDULER_SECRET
