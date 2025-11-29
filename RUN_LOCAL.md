# 🚀 Run Neuro Tutor Locally - Complete Guide

This guide provides **bulletproof, idiot-proof** instructions for running the complete Neuro Tutor stack on your local machine.

## 📋 Prerequisites

### Required Software
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download here](https://git-scm.com/downloads)
- **For local development (optional):**
  - **Node.js 18+** - [Download here](https://nodejs.org/)
  - **Python 3.11+** - [Download here](https://www.python.org/)

### Verify Installation
```bash
# Check Docker
docker --version
docker compose version

# Check Git
git --version

# For local dev (optional)
node --version
python --version
```

---

## 🎯 Method 1: Docker (Recommended)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd socratic-tutor
```

### Step 2: Create Environment File
```bash
# Copy the template
cp .env.example .env
```

### Step 3: Add OpenRouter API Key
1. Get your API key from [OpenRouter](https://openrouter.ai/keys)
2. Open `.env` file in a text editor
3. Replace the placeholder with your actual key:

```env
OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_API_KEY_HERE
```

### Step 4: Build and Start Services
```bash
# Build and start all services
docker compose up --build

# Or run in background
docker compose up --build -d
```

### Step 5: Access Applications
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Step 6: Stop Services (when done)
```bash
docker compose down
```

---

## 🛠️ Method 2: Local Development (Without Docker)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd socratic-tutor
```

### Step 2: Setup Backend
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Add your OpenRouter API key to .env file
# OPENROUTER_API_KEY=sk-or-v1-YOUR_ACTUAL_API_KEY_HERE

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### Step 3: Setup Frontend (New Terminal)
```bash
# Navigate to frontend
cd socratic-tutor-frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Add backend URL (usually default is fine)
# VITE_API_URL=http://localhost:8000

# Start frontend server
npm run dev
```

### Step 4: Access Applications
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## ✅ Verification Checklist

After starting the services, verify these work:

### 1. Basic Connectivity
- [ ] Frontend loads at http://localhost:5173
- [ ] Backend health check: http://localhost:8000/health
- [ ] API docs accessible: http://localhost:8000/docs

### 2. Chat Functionality
- [ ] Type a message in the chat interface
- [ ] Message sends successfully (see loading indicator)
- [ ] Receive AI response (not mock message)
- [ ] Check browser Network tab for POST to `/api/chat`

### 3. UI Features
- [ ] Theme toggle (light/dark) works
- [ ] Preferences drawer opens
- [ ] Can adjust verbosity level
- [ ] Can change explanation style
- [ ] Visual aids toggle works

### 4. Session Persistence
- [ ] Send a message
- [ ] Refresh the page
- [ ] Chat history persists
- [ ] New messages save to session

### 5. Socratic Methodology
- [ ] AI asks clarifying questions
- [ ] Responses are guided, not just answers
- [ ] Multiple-step explanations provided
- [ ] Preferences affect response style

---

## 🐛 Troubleshooting

### Docker Issues
```bash
# Reset everything
docker compose down -v
docker system prune -f
docker compose up --build
```

### Port Conflicts
If ports are in use:
```bash
# Kill processes on ports
# Windows:
netstat -ano | findstr :8000
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Backend Issues
```bash
# Check environment variables
docker exec projectrough-backend-1 printenv

# View backend logs
docker compose logs backend
```

### Frontend Issues
```bash
# Clear node modules and reinstall
cd socratic-tutor-frontend
rm -rf node_modules package-lock.json
npm install

# View frontend logs
docker compose logs frontend
```

### API Key Issues
1. Verify your OpenRouter API key is valid
2. Check that it's properly set in `.env` file
3. Restart services after updating the key

---

## 📝 Development Notes

- **Hot Reload:** Both frontend and backend support hot reload in development
- **Database:** SQLite database file created automatically in `backend/`
- **Logs:** Use `docker compose logs -f` to follow real-time logs
- **API Testing:** Use the Swagger UI at http://localhost:8000/docs

---

## 🎯 Success Criteria

You're successfully running Neuro Tutor when:

1. ✅ Both services start without errors
2. ✅ Frontend loads the chat interface
3. ✅ You can send and receive messages
4. ✅ AI responses follow Socratic methodology
5. ✅ All UI features work (themes, preferences)
6. ✅ Sessions persist across page refreshes

If all checklist items are marked, you're ready to use Neuro Tutor!
