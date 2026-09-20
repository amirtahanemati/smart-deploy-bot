from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from core.database import engine, Base
from bot.handlers import dp, bot
from api.webhook import router as notify_router

async def start_telegram_polling():
    """Start the aiogram polling process in the background."""
    await dp.start_polling(bot)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize SQLite database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Launch the Telegram bot polling in a separate background task
    polling_task = asyncio.create_task(start_telegram_polling())
    
    yield
    
    # 3. Gracefully shutdown the bot and close connections on exit
    polling_task.cancel()
    await bot.session.close()

app = FastAPI(title="Smart Deploy Central Bot", lifespan=lifespan)

# Register the webhook router
app.include_router(notify_router, prefix="/api")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "Smart Deploy Central Bot is Running"}