"""
Shared pytest fixtures for backend tests.
"""

import os

os.environ["TESTING"] = "1"

from datetime import datetime
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_db
from app.models import chat as chat_models  # noqa: F401
from app.models import subjects as subject_models  # noqa: F401
from app.models.chat import Message

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def configure_test_app():
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app)


@pytest.fixture
def db_session() -> Session:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    def fake_retrieve_context(query, subject_id):
        return [], []

    monkeypatch.setattr("app.api.chat.retrieve_context", fake_retrieve_context)
    monkeypatch.setattr("app.services.retrieval.retrieve_context", fake_retrieve_context)
    monkeypatch.setattr("app.services.subjects_service.delete_by_subject_id", lambda subject_id: None)
    monkeypatch.setattr("app.services.subjects_service.delete_by_material_id", lambda material_id: None)
    monkeypatch.setattr("app.api.subjects._run_ingestion", lambda material_id: None)

    async def fake_generate_response(messages, preferences=None, session_id=None, **kwargs):
        reply = Message(
            id=str(uuid.uuid4()),
            role="assistant",
            content="What do you already know about that topic?",
            timestamp=datetime.utcnow(),
        )
        return {
            "reply_message": reply,
            "session_id": session_id or str(uuid.uuid4()),
        }

    monkeypatch.setattr("app.api.chat.generate_response", fake_generate_response)

    async def fake_stream_response(messages, preferences=None, session_id=None, **kwargs):
        for token in ["What ", "do you ", "already know?"]:
            yield token

    monkeypatch.setattr("app.api.chat.stream_response", fake_stream_response)
