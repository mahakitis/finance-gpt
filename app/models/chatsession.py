from sqlalchemy import Column, String, DateTime
from app.db_utils.database import Base
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(String, primary_key=True, index=True) 
    created_at = Column(DateTime, default=datetime.utcnow)
