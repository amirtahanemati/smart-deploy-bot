from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base

class UserConnection(Base):
    __tablename__ = "user_connections"

    id = Column(Integer, primary_key=True, index=True)
    telegram_chat_id = Column(Integer, unique=True, index=True, nullable=False)
    pairing_code = Column(String(10), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)