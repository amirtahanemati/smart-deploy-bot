from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.user import UserConnection
from bot.handlers import bot
from config import settings

router = APIRouter()

# Data model for incoming deployment logs from the client package
class DeployLog(BaseModel):
    pairing_code: str
    message: str

@router.post("/notify")
async def send_notification(
    log_data: DeployLog, 
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Receive logs from client servers and route them to the correct Telegram user."""
    # Basic security layer to prevent unauthorized POST requests
    if authorization != f"Bearer {settings.WEBHOOK_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized client")

    # Retrieve the user's Chat ID based on the provided pairing code
    result = await db.execute(
        select(UserConnection).filter_by(pairing_code=log_data.pairing_code, is_active=True)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Pairing code not found or inactive")

    # Route the message to the user via Telegram
    try:
        await bot.send_message(chat_id=user.telegram_chat_id, text=log_data.message)
        return {"status": "success", "message": "Notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram API Error: {str(e)}")