"""
Shared chat session preparation for sync and streaming endpoints.
"""

from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chat import ChatRequest, Message, Preferences
from app.services.sessions import (
    create_session,
    get_session,
    get_session_messages,
    save_message,
    update_session_subject,
)


def prepare_chat_session(
    db: Session,
    request: ChatRequest,
) -> Tuple[str, List[Message], Preferences, Optional[str]]:
    """
    Resolve session, persist the latest user message, and build LLM history.

    Returns:
        Tuple of (session_id, message_history, preferences, subject_id)
    """
    if request.session_id:
        session = get_session(db, request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {request.session_id} not found",
            )
    else:
        title = "New Chat"
        if request.messages:
            user_msg = request.messages[-1]
            if user_msg.role == "user":
                title = user_msg.content[:50] + (
                    "..." if len(user_msg.content) > 50 else ""
                )
        session = create_session(db, title, subject_id=request.subject_id)

    if request.subject_id is not None:
        update_session_subject(db, session.id, request.subject_id)
        session = get_session(db, session.id)

    if request.messages:
        user_message = request.messages[-1]
        if user_message.role == "user":
            save_message(db, session.id, "user", user_message.content)

    existing_messages = get_session_messages(db, session.id)
    message_history = [
        Message(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp,
        )
        for msg in existing_messages
    ]

    preferences = request.preferences or Preferences()
    return session.id, message_history, preferences, session.subject_id
