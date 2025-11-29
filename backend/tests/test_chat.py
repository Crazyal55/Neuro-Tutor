"""
Tests for chat API with database persistence.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.core.db import Base, get_db
from app.models.chat import ChatSession, MessageModel
from app.services.sessions import create_session, get_session, list_sessions, save_message, get_session_messages


# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestChatAPI:
    """Test chat API endpoints."""
    
    def test_create_new_chat(self, client):
        """Test creating a new chat session."""
        request_data = {
            "messages": [
                {
                    "id": "msg1",
                    "role": "user", 
                    "content": "Hello, I need help with photosynthesis"
                }
            ],
            "preferences": {
                "verbosity_level": 3,
                "explanation_style": "step_by_step",
                "reading_mode": "comfortable",
                "visual_aids": True
            }
        }
        
        response = client.post("/api/chat/", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "reply_message" in data
        assert data["reply_message"]["role"] == "assistant"
        
        # Check session was created in database
        db = TestingSessionLocal()
        session = get_session(db, data["session_id"])
        assert session is not None
        assert session.title == "Hello, I need help with photosynthesis"
        db.close()
    
    def test_chat_with_existing_session(self, client, setup_test_database):
        """Test sending message to existing session."""
        # First, create a session
        db = TestingSessionLocal()
        session = create_session(db, "Test Session")
        session_id = session.id
        db.close()
        
        # Now send a message to that session
        request_data = {
            "session_id": session_id,
            "messages": [
                {
                    "id": "msg2",
                    "role": "user", 
                    "content": "Can you explain photosynthesis step by step?"
                }
            ]
        }
        
        response = client.post("/api/chat/", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "reply_message" in data
        
        # Check messages were saved
        db = TestingSessionLocal()
        messages = get_session_messages(db, session_id)
        assert len(messages) >= 2  # User message + AI response
        db.close()
    
    def test_get_sessions_list(self, client, setup_test_database):
        """Test listing all chat sessions."""
        db = TestingSessionLocal()
        
        # Create test sessions
        session1 = create_session(db, "Session 1")
        session2 = create_session(db, "Session 2")
        
        # Add messages to sessions
        save_message(db, session1.id, "user", "Test message 1")
        save_message(db, session1.id, "assistant", "Response 1")
        save_message(db, session2.id, "user", "Test message 2")
        
        db.close()
        
        response = client.get("/api/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert len(data["sessions"]) == 2
        
        # Check session data
        sessions = data["sessions"]
        session_ids = [s["id"] for s in sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
        
        # Check session summaries
        for session in sessions:
            assert "id" in session
            assert "title" in session
            assert "created_at" in session
            assert "last_updated_at" in session
            assert "message_count" in session
    
    def test_get_session_messages(self, client, setup_test_database):
        """Test getting messages for a specific session."""
        db = TestingSessionLocal()
        
        # Create test session with messages
        session = create_session(db, "Test Messages")
        save_message(db, session.id, "user", "First question")
        save_message(db, session.id, "assistant", "First answer")
        save_message(db, session.id, "user", "Follow-up question")
        session_id = session.id
        db.close()
        
        response = client.get(f"/api/chat/sessions/{session_id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "messages" in data
        assert len(data["messages"]) == 3
        
        # Check message order and content
        messages = data["messages"]
        assert messages[0]["role"] == "user"
        assert "First question" in messages[0]["content"]
        assert messages[1]["role"] == "assistant"
        assert "First answer" in messages[1]["content"]
        assert messages[2]["role"] == "user"
        assert "Follow-up question" in messages[2]["content"]
    
    def test_get_nonexistent_session_messages(self, client, setup_test_database):
        """Test getting messages for non-existent session."""
        fake_session_id = "nonexistent-session-id"
        
        response = client.get(f"/api/chat/sessions/{fake_session_id}/messages")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_chat_with_nonexistent_session(self, client, setup_test_database):
        """Test sending message to non-existent session."""
        fake_session_id = "nonexistent-session-id"
        request_data = {
            "session_id": fake_session_id,
            "messages": [
                {
                    "id": "msg3",
                    "role": "user", 
                    "content": "This should fail"
                }
            ]
        }
        
        response = client.post("/api/chat/", json=request_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_delete_session(self, client, setup_test_database):
        """Test deleting a session."""
        db = TestingSessionLocal()
        
        # Create test session
        session = create_session(db, "Session to Delete")
        session_id = session.id
        db.close()
        
        # Delete the session
        response = client.delete(f"/api/chat/sessions/{session_id}")
        
        assert response.status_code == 204
        
        # Verify session is deleted
        db = TestingSessionLocal()
        deleted_session = get_session(db, session_id)
        assert deleted_session is None
        db.close()
    
    def test_delete_welcome_session_fails(self, client, setup_test_database):
        """Test that welcome session cannot be deleted."""
        response = client.delete("/api/chat/sessions/welcome")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "cannot delete welcome session" in data["detail"].lower()


class TestSessionService:
    """Test session service functions."""
    
    def test_create_session_without_title(self, setup_test_database):
        """Test creating session without title generates default."""
        db = TestingSessionLocal()
        
        session = create_session(db)
        
        assert session is not None
        assert session.id is not None
        assert "Chat" in session.title
        db.close()
    
    def test_save_message_updates_timestamp(self, setup_test_database):
        """Test that saving message updates session timestamp."""
        db = TestingSessionLocal()
        
        # Create session
        original_session = create_session(db, "Timestamp Test")
        original_time = original_session.updated_at
        
        # Save a message after a delay
        import time
        time.sleep(0.1)
        
        save_message(db, original_session.id, "user", "Test message")
        
        # Refresh session from database
        updated_session = get_session(db, original_session.id)
        assert updated_session.updated_at > original_time
        db.close()


if __name__ == "__main__":
    pytest.main([__file__])
