from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str = "YOUR_BOT_TOKEN_HERE"
    DATABASE_URL: str = "sqlite+aiosqlite:///./smartdeploy.db"
    WEBHOOK_SECRET: str = "super_secret_key_for_clients"

    class Config:
        env_file = ".env"

settings = Settings()