"""
Pydantic and SQLAlchemy models for chat functionality.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base


class Message(BaseModel):
    """Represents a chat message."""
    id: str = Field(..., description="Unique message identifier")
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")


class Preferences(BaseModel):
    """User preferences for neurodivergent-friendly responses."""
    verbosity_level: int = Field(default=3, ge=1, le=5, description="Verbosity level (1-5)")
    explanation_style: Literal["concise", "step_by_step", "analogy"] = Field(
        default="step_by_step", 
        description="Style of explanation"
    )
    reading_mode: Literal["compact", "comfortable"] = Field(
        default="comfortable", 
        description="Reading format preference"
    )
    visual_aids: bool = Field(default=True, description="Whether to include visual aids")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    messages: List[Message] = Field(..., description="List of chat messages")
    preferences: Optional[Preferences] = Field(default=None, description="User preferences")
    session_id: Optional[str] = Field(default=None, description="Session identifier")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str = Field(..., description="Session identifier")
    reply_message: Message = Field(..., description="Assistant's reply message")


class SessionSummary(BaseModel):
    """Summary model for session listing."""
    id: str = Field(..., description="Session identifier")
    title: str = Field(..., description="Session title")
    created_at: datetime = Field(..., description="Session creation time")
    last_updated_at: datetime = Field(..., description="Last message time")
    message_count: int = Field(..., description="Number of messages in session")


class SessionListResponse(BaseModel):
    """Response model for sessions list endpoint."""
    sessions: List[SessionSummary] = Field(..., description="List of session summaries")


class SessionMessagesResponse(BaseModel):
    """Response model for session messages endpoint."""
    session_id: str = Field(..., description="Session identifier")
    messages: List[Message] = Field(..., description="Messages in this session")


# SQLAlchemy Models for Database
class ChatSession(Base):
    """SQLAlchemy model for chat sessions."""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship with messages
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id='{self.id}', title='{self.title}')>"


class MessageModel(Base):
    """SQLAlchemy model for messages."""
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with session
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<MessageModel(id='{self.id}', role='{self.role}', session_id='{self.session_id}')>"
