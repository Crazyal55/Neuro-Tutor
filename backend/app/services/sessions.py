"""
Database-backed session management for Neuro Tutor.
"""

import uuid
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.chat import ChatSession, MessageModel
from app.core.db import get_db


def create_session(db: Session, title: Optional[str] = None) -> ChatSession:
    """
    Create a new chat session.
    
    Args:
        db: Database session
        title: Optional session title
        
    Returns:
        ChatSession: Created session
    """
    session_id = str(uuid.uuid4())
    if not title:
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    db_session = ChatSession(
        id=session_id,
        title=title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session


def get_session(db: Session, session_id: str) -> Optional[ChatSession]:
    """
    Get a session by ID.
    
    Args:
        db: Database session
        session_id: Session identifier
        
    Returns:
        Optional[ChatSession]: Session if found, None otherwise
    """
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()


def list_sessions(db: Session) -> List[ChatSession]:
    """
    List all chat sessions.
    
    Args:
        db: Database session
        
    Returns:
        List[ChatSession]: All sessions ordered by last updated
    """
    return db.query(ChatSession).order_by(desc(ChatSession.updated_at)).all()


def save_message(db: Session, session_id: str, role: str, content: str) -> MessageModel:
    """
    Save a message to the database.
    
    Args:
        db: Database session
        session_id: Session identifier
        role: Message role ("user" or "assistant")
        content: Message content
        
    Returns:
        MessageModel: Saved message
    """
    message_id = str(uuid.uuid4())
    
    message = MessageModel(
        id=message_id,
        session_id=session_id,
        role=role,
        content=content,
        timestamp=datetime.utcnow()
    )
    
    # Update session timestamp
    session = get_session(db, session_id)
    if session:
        session.updated_at = datetime.utcnow()
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message


def get_session_messages(db: Session, session_id: str) -> List[MessageModel]:
    """
    Get all messages for a session.
    
    Args:
        db: Database session
        session_id: Session identifier
        
    Returns:
        List[MessageModel]: Messages ordered by timestamp
    """
    return db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).order_by(MessageModel.timestamp).all()


def get_session_message_count(db: Session, session_id: str) -> int:
    """
    Get message count for a session.
    
    Args:
        db: Database session
        session_id: Session identifier
        
    Returns:
        int: Number of messages
    """
    return db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).count()


def get_last_message_preview(db: Session, session_id: str, max_length: int = 50) -> str:
    """
    Get a preview of the last message in a session.
    
    Args:
        db: Database session
        session_id: Session identifier
        max_length: Maximum preview length
        
    Returns:
        str: Preview of last message
    """
    last_message = db.query(MessageModel).filter(
        MessageModel.session_id == session_id
    ).order_by(desc(MessageModel.timestamp)).first()
    
    if not last_message:
        return "No messages"
    
    content = last_message.content
    if len(content) > max_length:
        content = content[:max_length] + "..."
    
    return content


def delete_session(db: Session, session_id: str) -> bool:
    """
    Delete a session and all its messages.
    
    Args:
        db: Database session
        session_id: Session identifier
        
    Returns:
        bool: True if deleted, False if not found
    """
    session = get_session(db, session_id)
    if not session:
        return False
    
    db.delete(session)
    db.commit()
    return True
