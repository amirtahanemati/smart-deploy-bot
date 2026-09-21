from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()