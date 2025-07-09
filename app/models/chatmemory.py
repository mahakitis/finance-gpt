from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from app.db_utils.database import Base
from datetime import datetime

class ChatMemory(Base):
    __tablename__ = "memory_nodes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    sources = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
