"""
Chat API endpoints for Neuro Tutor.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.chat import (
    ChatRequest, 
    ChatResponse, 
    SessionListResponse, 
    SessionMessagesResponse,
    SessionSummary,
    Message
)
from app.services.llm_client import generate_response
from app.services.sessions import (
    create_session, 
    get_session, 
    list_sessions, 
    save_message,
    get_session_messages,
    get_session_message_count,
    get_last_message_preview,
    delete_session
)
from app.core.db import get_db


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """
    Main chat endpoint for Neuro Tutor.
    
    Processes user messages and generates neurodivergent-friendly responses.
    
    Args:
        request: Chat request with messages, preferences, and optional session_id
        db: Database session
        
    Returns:
        Chat response with session_id and assistant's reply
    """
    try:
        # Get or create session
        if request.session_id:
            session = get_session(db, request.session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session {request.session_id} not found"
                )
        else:
            # Create new session with title based on first message
            title = "New Chat"
            if request.messages:
                user_msg = request.messages[-1]
                if user_msg.role == "user":
                    # Use first 50 characters of user message as title
                    title = user_msg.content[:50] + ("..." if len(user_msg.content) > 50 else "")
            
            session = create_session(db, title)
        
        # Save user message to database
        if request.messages:
            user_message = request.messages[-1]  # Last message should be user message
            if user_message.role == "user":
                save_message(db, session.id, "user", user_message.content)
        
        # Get existing messages for context
        existing_messages = get_session_messages(db, session.id)
        
        # Convert to Message format for LLM client
        message_history = []
        for msg in existing_messages:
            message_history.append(Message(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            ))
        
        # Generate AI response
        response = await generate_response(message_history, request.preferences, session.id)
        reply_message = response["reply_message"]
        
        # Save AI reply to database
        saved_reply = save_message(db, session.id, "assistant", reply_message.content)
        
        # Convert to Message response format
        response_message = Message(
            id=saved_reply.id,
            role="assistant",
            content=reply_message.content,
            timestamp=saved_reply.timestamp
        )
        
        return ChatResponse(
            session_id=session.id,
            reply_message=response_message
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/sessions", response_model=SessionListResponse, status_code=status.HTTP_200_OK)
async def get_sessions(db: Session = Depends(get_db)) -> SessionListResponse:
    """
    Get list of all chat sessions.
    
    Returns:
        List of session summaries with metadata
    """
    try:
        db_sessions = list_sessions(db)
        
        # Convert to SessionSummary models
        session_summaries = []
        for session in db_sessions:
            message_count = get_session_message_count(db, session.id)
            last_preview = get_last_message_preview(db, session.id)
            
            summary = SessionSummary(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                last_updated_at=session.updated_at,
                message_count=message_count
            )
            session_summaries.append(summary)
        
        return SessionListResponse(sessions=session_summaries)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse, status_code=status.HTTP_200_OK)
async def get_session_messages_endpoint(session_id: str, db: Session = Depends(get_db)) -> SessionMessagesResponse:
    """
    Get all messages for a specific session.
    
    Args:
        session_id: Unique session identifier
        db: Database session
        
    Returns:
        Session messages
    """
    try:
        # Check if session exists
        session = get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Get messages from database
        db_messages = get_session_messages(db, session_id)
        
        # Convert to Message response format
        messages = []
        for msg in db_messages:
            message = Message(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp
            )
            messages.append(message)
        
        return SessionMessagesResponse(
            session_id=session_id,
            messages=messages
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session messages: {str(e)}"
        )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_endpoint(session_id: str, db: Session = Depends(get_db)) -> None:
    """
    Delete a specific session.
    
    Args:
        session_id: Unique session identifier
        db: Database session
    """
    try:
        if session_id == "welcome":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete welcome session"
            )
        
        success = delete_session(db, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )
