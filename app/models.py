# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String, index=True)
    ai_response = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())