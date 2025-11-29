# Neuro Tutor Backend

FastAPI backend for Neuro Tutor - an AI tutor specialized for neurodivergent students.

## Features

- 🧠 **Neurodivergent-friendly responses** with customizable teaching styles
- 🎯 **Socratic method** approach to encourage critical thinking
- 📝 **Session management** with conversation history
- 🎨 **Adjustable preferences**: verbosity, explanation style, visual aids
- 🔧 **Mock LLM responses** (ready for real LLM integration)
- 📚 **Clean architecture** with separation of concerns

## Tech Stack

- **FastAPI** - Modern, fast web framework for APIs
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **Python 3.11+** - Type hints and modern features

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   │   └── chat.py   # Chat and session endpoints
│   ├── core/          # Configuration
│   │   └── config.py  # Settings, CORS
│   ├── models/        # Pydantic models
│   │   └── chat.py   # Request/response models
│   ├── services/      # Business logic
│   │   ├── llm_client.py  # LLM abstraction (mock)
│   │   └── sessions.py    # Session management
│   └── main.py       # FastAPI app
├── tests/             # Test files
├── requirements.txt    # Dependencies
└── README.md         # This file
```

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Development Server

```bash
# Run with uvicorn (development mode)
uvicorn app.main:app --reload --port 8000

# Or run directly
python app/main.py
```

### 3. Access API

- **API**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`
- **Health**: `http://localhost:8000/health`

## API Endpoints

### Chat
- `POST /api/chat/` - Main chat endpoint
- `GET /api/chat/sessions` - List all sessions
- `GET /api/chat/sessions/{session_id}/messages` - Get session messages
- `DELETE /api/chat/sessions/{session_id}` - Delete session

### System
- `GET /` - Root info
- `GET /health` - Health check

## Usage Examples

### Chat Request

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"id": "1", "role": "user", "content": "How do Python loops work?"}
    ],
    "preferences": {
      "verbosity_level": 3,
      "explanation_style": "step_by_step",
      "reading_mode": "comfortable",
      "visual_aids": true
    }
  }'
```

### Response

```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "reply_message": {
    "id": "456e7890-e89b-12d3-a456-426614174001",
    "role": "assistant", 
    "content": "I see you're asking about Python loops. Let's break this down...",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Preferences

The API supports neurodivergent-friendly preferences:

- **verbosity_level**: 1-5 (1=very concise, 5=very detailed)
- **explanation_style**: `"concise"`, `"step_by_step"`, `"analogy"`
- **reading_mode**: `"compact"`, `"comfortable"`
- **visual_aids**: `true`/`false` (mentions visual assistance)

## Architecture Notes

### LLM Abstraction
The `services/llm_client.py` module provides a clean abstraction for LLM calls:

- Currently implements **mock responses**
- Easy to swap for real LLM (OpenAI, Claude, etc.)
- Maintains same interface for all LLM providers

### Session Management
The `services/sessions.py` module handles conversation state:

- **In-memory storage** (for development)
- Easy to replace with database persistence
- Automatic title generation from first user message
- Session isolation and lifecycle management

### Future-Proofing

The architecture is designed for easy upgrades:

1. **Real LLM Integration**: Modify only `services/llm_client.py`
2. **Database Persistence**: Replace in-memory storage in `services/sessions.py`
3. **Authentication**: Add middleware to `app/main.py`
4. **Rate Limiting**: Add middleware to control API usage

## Development

### Adding New Endpoints

1. Create Pydantic models in `app/models/`
2. Add business logic in `app/services/`
3. Create endpoint in `app/api/`
4. Register router in `app/main.py`

### Running Tests

```bash
# Run tests (when implemented)
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=app
```

## Configuration

Environment variables (create `.env` file):

```bash
DEBUG=false
CORS_ORIGINS=http://localhost:5173,http://localhost:5177
```

## Production Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Traditional

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Contributing

1. Follow the existing code style
2. Add type hints everywhere
3. Include docstrings for public functions
4. Write tests for new features
5. Keep the architecture clean

## License

MIT License - see LICENSE file for details.
