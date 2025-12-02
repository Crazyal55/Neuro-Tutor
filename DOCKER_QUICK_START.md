# Docker Quick Start Guide

## 🚀 One-Command Docker Setup

### Prerequisites
- Docker Desktop installed and running
- Your OpenRouter API key

### Quick Start Commands

```bash
# 1. Copy environment template
cp .env.docker.example .env

# 2. Edit your API key
# Edit .env file and replace YOUR_OPENROUTER_API_KEY_HERE with your actual key

# 3. Build and run
docker compose up --build

# 4. Access application
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

### What Happens Behind the Scenes

1. **Build Phase**: Docker builds images from Dockerfiles
2. **Network Creation**: Creates isolated network for containers
3. **Container Startup**: Backend starts first, frontend waits
4. **Health Checks**: Both containers verify they're healthy
5. **Service Ready**: Frontend connects to backend via internal network

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| OPENROUTER_API_KEY | OpenRouter access | sk-or-v1-abc123... |
| DEFAULT_MODEL | AI model to use | openai/gpt-3.5-turbo |
| DATABASE_URL | Database location | sqlite:///./data/neuro_tutor.db |

### Verification Commands

```bash
# Check container status
docker compose ps

# View logs
docker compose logs

# Test health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:5173

# Stop services
docker compose down

# Restart services
docker compose restart
```

### Common Issues & Solutions

**Issue**: "Port already in use"
- **Solution**: `docker compose down` then `docker compose up --build`

**Issue**: "API key not found"
- **Solution**: Ensure `.env` file is in project root with correct key

**Issue**: "Frontend can't reach backend"
- **Solution**: Check if both containers are running: `docker compose ps`

### Success Indicators

✅ **Backend**: Healthy response from http://localhost:8000/health  
✅ **Frontend**: React app loads at http://localhost:5173  
✅ **Chat**: AI responses without "trouble connecting" messages  
✅ **Docker**: Both containers show "Running" in Docker Desktop

### Development Workflow

```bash
# Development with live reload
docker compose up --build

# Make changes to code
# Edit files in project directory

# Containers auto-reload
# No need to restart for most changes
```

### Production Workflow

```bash
# Production deployment
docker compose -f docker-compose.yml up --build -d

# View logs
docker compose logs -f

# Scale services
docker compose up --scale backend=2
```

---

**🎯 Result**: Full Docker setup with automated health checks, environment variable management, and verified OpenRouter integration.
