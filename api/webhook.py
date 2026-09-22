from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from models.user import UserConnection
from bot.handlers import bot

router = APIRouter()

class DeployLog(BaseModel):
    pairing_code: str
    message: str

@router.post("/notify")
async def send_notification(
    log_data: DeployLog, 
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Receive logs from client servers and validate Dynamic Magic Tokens."""
    
    # 1. Validate the presence of Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token format")
        
    provided_secret = authorization.split(" ")[1]

    # 2. Dynamic Security Check: Match BOTH pairing_code and secret_key
    result = await db.execute(
        select(UserConnection).filter_by(
            pairing_code=log_data.pairing_code,
            secret_key=provided_secret,
            is_active=True
        )
    )
    user = result.scalar_one_or_none()

    # 3. Reject if credentials don't match or server is inactive
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials or inactive server")

    # 4. Route the message to the specific user via Telegram
    try:
        await bot.send_message(chat_id=user.telegram_chat_id, text=log_data.message)
        return {"status": "success", "message": "Notification routed securely"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telegram API Error: {str(e)}")