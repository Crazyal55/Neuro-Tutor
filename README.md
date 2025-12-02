# Neuro Tutor - Socratic Learning Assistant

A neurodivergent-friendly Socratic learning assistant that guides students through discovery-based learning using thoughtful questioning and personalized teaching approaches.

## 🌟 Features

- **Socratic Methodology**: Guides learning through questions rather than direct answers
- **Neurodivergent-Friendly**: Adaptable learning styles and pacing
- **Real-time Chat**: Interactive conversations with AI-powered responses
- **Session Management**: Persistent chat sessions with automatic saving
- **Theme Support**: Light/dark mode with comfortable reading options
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Modern Stack**: Built with React 19, FastAPI, and Tailwind CSS v3

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/get-started/) (recommended) or Node.js 18+ and Python 3.9+
- [OpenRouter API Key](https://openrouter.ai/) for AI responses

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Crazyal55/Neuro-Tutor.git
   cd "Project Rough"
   ```

2. **Configure OpenRouter API Key**:
   ```bash
   # Create backend/.env file
   cp backend/.env.example backend/.env
   
   # Edit backend/.env and add your API key
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   DEFAULT_MODEL=anthropic/claude-3-haiku
   ```

3. **Start the application**:
   ```bash
   docker compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env and add OPENROUTER_API_KEY
   
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend Setup**:
   ```bash
   cd socratic-tutor-frontend
   npm install
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

## 🧪 Testing Integration

### Verify Everything Works

1. **Check Services**:
   ```bash
   # Docker
   docker compose ps
   
   # Should show both services as "healthy"
   ```

2. **Test Backend**:
   - Visit http://localhost:8000/health
   - Should return `{"status": "healthy", "service": "Neuro Tutor", "version": "1.0.0"}`

3. **Test Frontend**:
   - Open http://localhost:5173
   - Interface should load with chat functionality, theme toggle, and preferences drawer

4. **Test AI Integration**:
   - Open browser Developer Tools (F12) → Network tab
   - Send a message: "Why does the moon cause tides?"
   - Verify POST request to `/api/chat`
   - **Important**: Response should NOT be "This is a test response from mock Socratic Tutor. 😊"
   - Should receive thoughtful Socratic questions from OpenRouter

### Expected Behavior

✅ **Working Correctly**:
- Messages trigger network requests to backend
- AI responses use Socratic methodology (asking questions, not giving answers)
- Session persistence across page refreshes
- Loading states with typing indicators while waiting for responses
- Theme toggle between light and dark modes
- User preferences (verbosity, explanation style, reading mode) are saved
- User-friendly error messages

❌ **Common Issues**:
- **Mock responses**: Check if API key is set correctly
- **CORS errors**: Ensure backend is running and accessible
- **Instant responses**: Still using mock data instead of real API
- **No network requests**: Frontend not connected to backend

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI 0.104.1 with async support
- **AI Integration**: OpenRouter API with Socratic methodology
- **Database**: SQLAlchemy 2.0.23 with SQLite for session management
- **Dependencies**: Pydantic 2.0.3, uvicorn 0.24.0, python-dotenv 1.0.0

### Frontend (React + TypeScript)
- **Framework**: Vite 5.4.14 + React 19.2.0
- **UI Library**: shadcn/ui components + Tailwind CSS 3.4.18
- **State Management**: React hooks with localStorage for persistence
- **Key Dependencies**: 
  - Radix UI components (checkbox, dialog, icons, label, scroll-area, select, slider, slot)
  - Lucide React 0.554.0 for icons
  - clsx 2.1.1 and tailwind-merge 3.4.0 for styling

### Key Components
```
socratic-tutor-frontend/
├── src/
│   ├── components/
│   │   ├── chat/           # Chat interface components
│   │   │   ├── ChatInput.tsx     # Message input component
│   │   │   ├── ChatSidebar.tsx   # Session history sidebar
│   │   │   ├── MessageBubble.tsx # Individual message display
│   │   │   ├── MessageList.tsx   # Conversation container
│   │   │   └── TypingIndicator.tsx # Loading indicator
│   │   ├── layout/          # Header, sidebar, theming
│   │   │   ├── Header.tsx         # Main app header
│   │   │   ├── PreferencesDrawer.tsx # Settings panel
│   │   │   └── ThemeToggle.tsx    # Dark/light mode switcher
│   │   ├── ui/            # shadcn/ui components
│   │   │   ├── button.tsx, checkbox.tsx, input.tsx, label.tsx
│   │   │   ├── scroll-area.tsx, select.tsx, sheet.tsx, slider.tsx
│   │   │   └── ... (other UI primitives)
│   │   └── ThemeProvider.tsx # Global theme context
│   ├── services/
│   │   └── chatService.ts   # API client layer for backend communication
│   ├── pages/
│   │   └── ChatPage.tsx     # Main application page
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   └── App.jsx              # Root application component
```

```
backend/
├── app/
│   ├── api/
│   │   └── chat.py          # Chat API endpoints
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   ├── db.py           # Database setup and session management
│   │   └── openrouter_secrets.py # API key management
│   ├── models/
│   │   └── chat.py          # Database models for sessions and messages
│   ├── services/
│   │   ├── llm_client.py    # OpenRouter API integration
│   │   └── sessions.py      # Session management logic
│   └── main.py              # FastAPI application entry point
├── tests/
│   └── test_chat.py         # Test suite for chat functionality
└── requirements.txt         # Python dependencies
```

## 📚 How It Works

### Socratic Methodology
The AI tutor follows these principles:

1. **Never Give Direct Answers**: Instead responds with guiding questions
2. **Build on Prior Knowledge**: Asks about what the student already knows
3. **Step-by-Step Reasoning**: Breaks down complex topics
4. **Personalized Pacing**: Adapts to student's learning speed
5. **Neurodivergent-Friendly**: Clear, structured communication

### Example Interaction
```
Student: "Why does the moon cause tides?"
Tutor: "That's a great question! Let's think about this together. 
Have you noticed that the moon's gravity affects Earth? 
What do you know about how gravity works between objects?"
```

## 🔧 Configuration

### Environment Variables

**Backend (backend/.env)**:
```bash
OPENROUTER_API_KEY=your_api_key_here
DEFAULT_MODEL=anthropic/claude-3-haiku
DATABASE_URL=sqlite:///./data/neuro_tutor.db  # Default SQLite
DEBUG=true
```

**Frontend (socratic-tutor-frontend/.env)**:
```bash
VITE_API_URL=http://localhost:8000
```

### Customization

You can customize the AI behavior through the preferences panel (accessible via the settings button in the header):
- **Verbosity Level**: How detailed responses should be (slider control)
- **Explanation Style**: Concise, step-by-step, or analogy-based (select dropdown)
- **Reading Mode**: Compact or comfortable spacing (checkbox)
- **Visual Aids**: Include diagrams and examples (checkbox)

## 🐛 Troubleshooting

### Common Issues

**"Mock response" appearing**:
```bash
# Check API key is set
cat backend/.env | grep OPENROUTER_API_KEY

# Test API key directly
cd backend && python test_openrouter.py
```

**CORS errors**:
- Ensure backend is running on port 8000
- Check frontend VITE_API_URL points to correct backend
- Restart both services with `docker compose up --build`

**Frontend not loading**:
- Check if port 5173 is available
- Try `npm run dev` in frontend directory
- Clear browser cache and localStorage

**Backend connection failed**:
- Verify OpenRouter API key is valid
- Check internet connection
- View backend logs: `docker compose logs backend`

### Getting Help

1. Check the [PROGRESS.md](PROGRESS.md) for current development status
2. Review [FRONTEND.md](FRONTEND.md) for frontend-specific setup
3. Review [BACKEND.md](BACKEND.md) for backend-specific setup
4. Check [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for API key help
5. See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing procedures
6. Reference [FILE_STRUCTURE.md](FILE_STRUCTURE.md) for complete project structure
7. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guide

## 🤝 Contributing

This project is designed to be neurodivergent-friendly and inclusive. When contributing:

1. Follow the Socratic methodology in AI responses
2. Ensure UI is accessible and user-friendly
3. Test with different learning preferences
4. Maintain clear, simple communication
5. Use TypeScript for frontend development
6. Follow existing code patterns and component structure

## 📄 License

[License information here]

---

**Ready to start learning?** Open http://localhost:5173 and begin your Socratic journey! 🚀

## 📊 Current Status

This is an actively developed project with:
- ✅ Working Docker Compose setup
- ✅ Functional React 19 + Vite frontend
- ✅ FastAPI backend with OpenRouter integration
- ✅ Session persistence and theme support
- ✅ Responsive design with shadcn/ui components
- ✅ Comprehensive error handling and logging

The application is ready for testing and further development.
