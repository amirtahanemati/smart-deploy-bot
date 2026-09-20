from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.database import engine, Base
from bot.handlers import dp, bot
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await bot.session.close()

app = FastAPI(title="Smart Deploy Bot API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "Smart Deploy Bot Central Server is Running"}