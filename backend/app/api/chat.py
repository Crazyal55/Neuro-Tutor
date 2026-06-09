"""
Chat API endpoints for Neuro Tutor.
"""

import json
import logging

from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import get_db
from app.core.rate_limit import limiter
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    SessionListResponse,
    SessionMessagesResponse,
    SessionSummary,
    SessionUpdateRequest,
    Message,
)
from app.services.llm_client import generate_response, stream_response
from app.services.chat_flow import prepare_chat_session
from app.services.retrieval import build_rag_prompt_section, retrieve_context
from app.services.sessions import (
    get_session,
    list_sessions,
    save_message,
    get_session_messages,
    get_session_message_count,
    get_last_message_preview,
    update_session_title,
    delete_session,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def _format_sse(event_type: str, payload: dict) -> str:
    return f"data: {json.dumps({'type': event_type, **payload})}\n\n"


def _build_rag(subject_id: str | None, message_history: list[Message]):
    if not subject_id or not message_history:
        return "", []

    user_messages = [message for message in message_history if message.role == "user"]
    if not user_messages:
        return "", []

    hits, sources = retrieve_context(user_messages[-1].content, subject_id)
    return build_rag_prompt_section(hits), sources


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Main chat endpoint — returns a complete assistant reply."""
    try:
        session_id, message_history, preferences, subject_id = prepare_chat_session(
            db, chat_request
        )
        rag_context, sources = _build_rag(subject_id, message_history)
        response = await generate_response(
            message_history,
            preferences,
            session_id,
            rag_context=rag_context,
        )
        reply_message = response["reply_message"]

        saved_reply = save_message(db, session_id, "assistant", reply_message.content)
        response_message = Message(
            id=saved_reply.id,
            role="assistant",
            content=reply_message.content,
            timestamp=saved_reply.timestamp,
        )

        return ChatResponse(
            session_id=session_id,
            reply_message=response_message,
            sources=sources,
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(error)}",
        ) from error


@router.post("/stream")
@limiter.limit("20/minute")
async def chat_stream_endpoint(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Stream assistant reply tokens via Server-Sent Events."""
    try:
        session_id, message_history, preferences, subject_id = prepare_chat_session(
            db, chat_request
        )
        rag_context, sources = _build_rag(subject_id, message_history)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error preparing chat stream: {str(error)}",
        ) from error

    persist_session_factory = sessionmaker(bind=db.get_bind())

    async def event_generator():
        full_content = ""
        try:
            async for token in stream_response(
                message_history,
                preferences,
                session_id,
                rag_context=rag_context,
            ):
                full_content += token
                yield _format_sse("token", {"content": token})

            persist_db = persist_session_factory()
            try:
                saved_reply = save_message(
                    persist_db,
                    session_id,
                    "assistant",
                    full_content,
                )
                reply_message = Message(
                    id=saved_reply.id,
                    role="assistant",
                    content=full_content,
                    timestamp=saved_reply.timestamp,
                )
                yield _format_sse(
                    "done",
                    {
                        "session_id": session_id,
                        "reply_message": reply_message.model_dump(mode="json"),
                        "sources": [source.model_dump(mode="json") for source in sources],
                    },
                )
            finally:
                persist_db.close()
        except Exception as error:
            logger.exception("Chat stream failed for session %s", session_id)
            yield _format_sse("error", {"detail": str(error)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions", response_model=SessionListResponse, status_code=status.HTTP_200_OK)
async def get_sessions(db: Session = Depends(get_db)) -> SessionListResponse:
    """Get list of all chat sessions."""
    try:
        db_sessions = list_sessions(db)
        session_summaries = []
        for session in db_sessions:
            message_count = get_session_message_count(db, session.id)
            last_preview = get_last_message_preview(db, session.id)

            summary = SessionSummary(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                last_updated_at=session.updated_at,
                message_count=message_count,
                last_message_preview=last_preview,
                subject_id=session.subject_id,
            )
            session_summaries.append(summary)

        return SessionListResponse(sessions=session_summaries)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sessions: {str(error)}",
        ) from error


@router.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse, status_code=status.HTTP_200_OK)
async def get_session_messages_endpoint(session_id: str, db: Session = Depends(get_db)) -> SessionMessagesResponse:
    """Get all messages for a specific session."""
    try:
        session = get_session(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        db_messages = get_session_messages(db, session_id)
        messages = [
            Message(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
            )
            for msg in db_messages
        ]

        return SessionMessagesResponse(session_id=session_id, messages=messages)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session messages: {str(error)}",
        ) from error


@router.patch("/sessions/{session_id}", response_model=SessionSummary, status_code=status.HTTP_200_OK)
async def update_session_endpoint(
    session_id: str,
    request: SessionUpdateRequest,
    db: Session = Depends(get_db),
) -> SessionSummary:
    """Rename a chat session."""
    try:
        session = update_session_title(db, session_id, request.title)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        return SessionSummary(
            id=session.id,
            title=session.title,
            created_at=session.created_at,
            last_updated_at=session.updated_at,
            message_count=get_session_message_count(db, session.id),
            last_message_preview=get_last_message_preview(db, session.id),
            subject_id=session.subject_id,
        )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating session: {str(error)}",
        ) from error


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_endpoint(session_id: str, db: Session = Depends(get_db)) -> None:
    """Delete a specific session."""
    try:
        if session_id == "welcome":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete welcome session",
            )

        success = delete_session(db, session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(error)}",
        ) from error
