import json
import base64
import uuid
import random
import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from models.user import UserConnection
from config import settings

bot = Bot(
    token=settings.BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 <b>Welcome to Smart Deploy Notification Bot!</b>\n\n"
        "I will send you real-time deployment logs from your servers.\n\n"
        "To connect a new server to this chat, simply send:\n"
        "👉 /new_server"
    )
    await message.answer(welcome_text)

@dp.message(Command("new_server"))
async def cmd_new_server(message: types.Message):
    """Generate a Magic Token to link a new server securely."""
    chat_id = message.chat.id
    
    # 1. Generate unique credentials
    characters = string.ascii_uppercase + string.digits
    pairing_code = ''.join(random.choices(characters, k=6))
    secret_key = f"sd_{uuid.uuid4().hex}"
    
    # 2. Save securely to Database
    async with AsyncSessionLocal() as session:
        new_connection = UserConnection(
            telegram_chat_id=chat_id,
            pairing_code=pairing_code,
            secret_key=secret_key,
            is_active=True
        )
        session.add(new_connection)
        await session.commit()
        
    # 3. Create the Magic Token (Base64)
    token_data = {
        "url": settings.CENTRAL_API_URL,
        "secret": secret_key,
        "pairing_code": pairing_code
    }
    token_json = json.dumps(token_data)
    magic_token = base64.b64encode(token_json.encode('utf-8')).decode('utf-8')
    
    # 4. Send instructions to the user
    response_text = (
        f"✅ <b>Server Credentials Generated!</b>\n\n"
        f"To securely link your server, copy and run this exact command in your server's terminal:\n\n"
        f"<code>smart-deploy bot link {magic_token}</code>\n\n"
        f"<i>Pairing Code: {pairing_code}</i>"
    )
    await message.answer(response_text)