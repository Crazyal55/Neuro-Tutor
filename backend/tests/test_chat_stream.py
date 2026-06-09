"""Tests for streaming chat endpoint."""

from fastapi.testclient import TestClient


class TestChatStreamAPI:
    def test_stream_chat_returns_sse_events(self, client: TestClient):
        request_data = {
            "messages": [
                {
                    "id": "msg-stream",
                    "role": "user",
                    "content": "Tell me about gravity",
                }
            ],
        }

        with client.stream("POST", "/api/chat/stream", json=request_data) as response:
            assert response.status_code == 200
            body = "".join(response.iter_text())

        assert '"type": "token"' in body
        assert '"type": "done"' in body
        assert "session_id" in body
