# Neuro Tutor - Socratic Learning Assistant

A neurodivergent-friendly Socratic learning assistant that guides students through discovery-based learning using thoughtful questioning and personalized teaching approaches.

## 🌟 Features

- **Socratic Methodology**: Guides learning through questions rather than direct answers
- **Neurodivergent-Friendly**: Adaptable learning styles and pacing
- **Real-time Chat**: Interactive conversations with AI-powered responses
- **Session Management**: Persistent chat sessions with automatic saving
- **Theme Support**: Light/dark mode with comfortable reading options
- **Responsive Design**: Works seamlessly on desktop and mobile

## 🚀 Quick Start

### Prerequisites

- [Docker](https://www.docker.com/get-started/) (recommended) or Node.js 18+ and Python 3.9+
- [OpenRouter API Key](https://openrouter.ai/) for AI responses

### Option 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd neuro-tutor
   ```

2. **Configure OpenRouter API Key**:
   ```bash
   # Create backend/.env file
   cp backend/.env.example backend/.env
   
   # Edit backend/.env and add your API key
   OPENROUTER_API_KEY=your_openrouter_api_key_here
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
   - Frontend: http://localhost:5180
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
   - Should return "OK" status

3. **Test Frontend**:
   - Open http://localhost:5173 (Docker) or http://localhost:5180 (Local)
   - Interface should load with chat functionality

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
- Loading states while waiting for responses
- User-friendly error messages

❌ **Common Issues**:
- **Mock responses**: Check if API key is set correctly
- **CORS errors**: Ensure backend is running and accessible
- **Instant responses**: Still using mock data instead of real API
- **No network requests**: Frontend not connected to backend

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **AI Integration**: OpenRouter API with Socratic methodology
- **Database**: SQLAlchemy with session management
- **Authentication**: JWT-based (planned)

### Frontend (React + TypeScript)
- **Framework**: Vite + React 18 + TypeScript
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: React hooks with localStorage
- **Styling**: Tailwind CSS with theme support

### Key Components
```
socratic-tutor-frontend/
├── src/
│   ├── components/
│   │   ├── chat/           # Chat interface components
│   │   ├── layout/          # Header, sidebar, theming
│   │   └── ui/            # shadcn/ui components
│   ├── services/
│   │   └── chatService.ts   # API client layer
│   └── pages/
│       └── ChatPage.tsx     # Main application page
```

```
backend/
├── app/
│   ├── api/                 # API endpoints
│   ├── core/                # Configuration, secrets
│   ├── models/              # Database models
│   └── services/            # Business logic
└── tests/                  # Test suite
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

**Backend (.env)**:
```bash
OPENROUTER_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./neuro_tutor.db  # Default SQLite
DEBUG=true
```

**Frontend (.env)**:
```bash
VITE_API_URL=http://localhost:8000
```

### Customization

You can customize the AI behavior through the preferences panel:
- **Verbosity Level**: How detailed responses should be
- **Explanation Style**: Concise, step-by-step, or analogy-based
- **Reading Mode**: Compact or comfortable spacing
- **Visual Aids**: Include diagrams and examples

## 🐛 Troubleshooting

### Common Issues

**"Mock response" appearing**:
```bash
# Check API key is set
echo $OPENROUTER_API_KEY  # Should show your key

# Or check .env file
cat backend/.env
```

**CORS errors**:
- Ensure backend is running on port 8000
- Check frontend VITE_API_URL points to correct backend
- Restart both services

**Frontend not loading**:
- Check if port 5173 is available
- Try `npm run dev` in frontend directory
- Clear browser cache

**Backend connection failed**:
- Verify OpenRouter API key is valid
- Check internet connection
- View backend logs: `docker compose logs backend`

### Getting Help

1. Check the [PROGRESS.md](PROGRESS.md) for current development status
2. Review [FRONTEND.md](FRONTEND.md) for frontend-specific setup
3. Review [BACKEND.md](BACKEND.md) for backend-specific setup
4. Check [OPENROUTER_SETUP.md](OPENROUTER_SETUP.md) for API key help

## 🤝 Contributing

This project is designed to be neurodivergent-friendly and inclusive. When contributing:

1. Follow the Socratic methodology in AI responses
2. Ensure UI is accessible and user-friendly
3. Test with different learning preferences
4. Maintain clear, simple communication

## 📄 License

[License information here]

---

**Ready to start learning?** Open http://localhost:5173 and begin your Socratic journey! 🚀
