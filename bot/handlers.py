from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from models.user import UserConnection
from config import settings

# Initialize bot and dispatcher
bot = Bot(
    token=settings.BOT_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handle the /start command and send welcome instructions."""
    welcome_text = (
        "👋 <b>Welcome to the Smart Deploy Notification Bot!</b>\n\n"
        "This bot will send you real-time deployment logs and status alerts from your servers.\n\n"
        "To connect your server, first run this command in your server terminal:\n"
        "<code>smart-deploy bot connect</code>\n\n"
        "Then, send the generated 6-digit code here using the following format:\n"
        "<code>/connect YOUR_CODE</code>"
    )
    await message.answer(welcome_text)

@dp.message(Command("connect"))
async def cmd_connect(message: types.Message):
    """Handle the /connect command to pair a user's chat ID with their server."""
    # Extract the pairing code from the command (e.g., /connect A7X9Q2)
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("⚠️ Invalid format. Please send the code like this:\n<code>/connect 123456</code>")
        
    pairing_code = parts[1].upper()
    chat_id = message.chat.id

    async with AsyncSessionLocal() as session:
        # Check if this chat ID is already connected to a server
        result = await session.execute(select(UserConnection).filter_by(telegram_chat_id=chat_id))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Update the existing connection with the new pairing code
            existing_user.pairing_code = pairing_code
            existing_user.is_active = True
        else:
            # Create a new connection record
            new_connection = UserConnection(
                telegram_chat_id=chat_id,
                pairing_code=pairing_code,
                is_active=True
            )
            session.add(new_connection)
            
        await session.commit()
        
    success_text = (
        f"✅ <b>Connection Successful!</b>\n"
        f"Server Pairing Code: <code>{pairing_code}</code>\n\n"
        "You will now receive all deployment logs from this server directly in this chat."
    )
    await message.answer(success_text)