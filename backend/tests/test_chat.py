"""
Tests for chat API with database persistence.
"""

import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.sessions import (
    create_session,
    get_session,
    list_sessions,
    save_message,
    get_session_messages,
)

MOCK_REPLY = "What do you already know about that topic?"


class TestChatAPI:
    """Test chat API endpoints."""

    def test_create_new_chat(self, client: TestClient, db_session: Session):
        request_data = {
            "messages": [
                {
                    "id": "msg1",
                    "role": "user",
                    "content": "Hello, I need help with photosynthesis",
                }
            ],
            "preferences": {
                "verbosity_level": 3,
                "explanation_style": "step_by_step",
                "reading_mode": "comfortable",
                "visual_aids": True,
            },
        }

        response = client.post("/api/chat/", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "reply_message" in data
        assert data["reply_message"]["role"] == "assistant"
        assert data["reply_message"]["content"] == MOCK_REPLY

        session = get_session(db_session, data["session_id"])
        assert session is not None
        assert session.title == "Hello, I need help with photosynthesis"

    def test_chat_with_existing_session(self, client: TestClient, db_session: Session):
        session = create_session(db_session, "Test Session")
        session_id = session.id

        request_data = {
            "session_id": session_id,
            "messages": [
                {
                    "id": "msg2",
                    "role": "user",
                    "content": "Can you explain photosynthesis step by step?",
                }
            ],
        }

        response = client.post("/api/chat/", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["reply_message"]["content"] == MOCK_REPLY

        messages = get_session_messages(db_session, session_id)
        assert len(messages) >= 2

    def test_get_sessions_list(self, client: TestClient, db_session: Session):
        session1 = create_session(db_session, "Session 1")
        session2 = create_session(db_session, "Session 2")

        save_message(db_session, session1.id, "user", "Test message 1")
        save_message(db_session, session1.id, "assistant", "Response 1")
        save_message(db_session, session2.id, "user", "Test message 2")

        response = client.get("/api/chat/sessions")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) == 2

        session_ids = [session["id"] for session in data["sessions"]]
        assert session1.id in session_ids
        assert session2.id in session_ids

        for session in data["sessions"]:
            assert "id" in session
            assert "title" in session
            assert "created_at" in session
            assert "last_updated_at" in session
            assert "message_count" in session
            assert "last_message_preview" in session

    def test_get_session_messages(self, client: TestClient, db_session: Session):
        session = create_session(db_session, "Test Messages")
        save_message(db_session, session.id, "user", "First question")
        save_message(db_session, session.id, "assistant", "First answer")
        save_message(db_session, session.id, "user", "Follow-up question")
        session_id = session.id

        response = client.get(f"/api/chat/sessions/{session_id}/messages")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert len(data["messages"]) == 3

        messages = data["messages"]
        assert messages[0]["role"] == "user"
        assert "First question" in messages[0]["content"]
        assert messages[1]["role"] == "assistant"
        assert "First answer" in messages[1]["content"]
        assert messages[2]["role"] == "user"
        assert "Follow-up question" in messages[2]["content"]

    def test_get_nonexistent_session_messages(self, client: TestClient):
        response = client.get("/api/chat/sessions/nonexistent-session-id/messages")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_chat_with_nonexistent_session(self, client: TestClient):
        request_data = {
            "session_id": "nonexistent-session-id",
            "messages": [
                {
                    "id": "msg3",
                    "role": "user",
                    "content": "This should fail",
                }
            ],
        }

        response = client.post("/api/chat/", json=request_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_session(self, client: TestClient, db_session: Session):
        session = create_session(db_session, "Session to Delete")
        session_id = session.id

        response = client.delete(f"/api/chat/sessions/{session_id}")

        assert response.status_code == 204
        assert get_session(db_session, session_id) is None

    def test_delete_welcome_session_fails(self, client: TestClient):
        response = client.delete("/api/chat/sessions/welcome")

        assert response.status_code == 400
        assert "cannot delete welcome session" in response.json()["detail"].lower()

    def test_update_session_title(self, client: TestClient, db_session: Session):
        session = create_session(db_session, "Old Title")

        response = client.patch(
            f"/api/chat/sessions/{session.id}",
            json={"title": "Renamed Session"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Renamed Session"
        assert data["last_message_preview"] == "No messages"

    def test_update_nonexistent_session(self, client: TestClient):
        response = client.patch(
            "/api/chat/sessions/nonexistent-session-id",
            json={"title": "Missing"},
        )

        assert response.status_code == 404


class TestSessionService:
    """Test session service functions."""

    def test_create_session_without_title(self, db_session: Session):
        session = create_session(db_session)

        assert session is not None
        assert session.id is not None
        assert "Chat" in session.title

    def test_save_message_updates_timestamp(self, db_session: Session):
        original_session = create_session(db_session, "Timestamp Test")
        original_time = original_session.updated_at

        time.sleep(0.1)
        save_message(db_session, original_session.id, "user", "Test message")

        updated_session = get_session(db_session, original_session.id)
        assert updated_session.updated_at > original_time

    def test_list_sessions_returns_created_sessions(self, db_session: Session):
        create_session(db_session, "Alpha")
        create_session(db_session, "Beta")

        sessions = list_sessions(db_session)
        titles = [session.title for session in sessions]

        assert "Alpha" in titles
        assert "Beta" in titles


if __name__ == "__main__":
    pytest.main([__file__])
