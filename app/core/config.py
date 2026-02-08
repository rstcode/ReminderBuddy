from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./reminder.db"
    TELEGRAM_BOT_TOKEN: str = ""
    SCHEDULER_SECRET: str = "supersecretkey"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

