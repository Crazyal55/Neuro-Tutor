# Neuro Tutor Deployment Guide

This guide covers how to run and deploy the Neuro Tutor application both locally and using Docker.

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone and navigate to project
git clone <repository-url>
cd neuro-tutor

# Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your OpenRouter API key

# Run with Docker Compose
docker-compose up --build
```

Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend Setup
cd ../socratic-tutor-frontend
npm install

# Set environment variables
# Copy backend/.env.example to backend/.env and add your OpenRouter API key

# Start Backend (Terminal 1)
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start Frontend (Terminal 2)
cd ../socratic-tutor-frontend
npm run dev
```

## 📋 Prerequisites

### Required
- **Docker & Docker Compose** (for containerized deployment)
- **Node.js 18+** (for local frontend development)
- **Python 3.11+** (for local backend development)
- **OpenRouter API Key** (for AI functionality)

### OpenRouter API Setup
1. Visit [OpenRouter.ai](https://openrouter.ai/keys)
2. Create an account and generate an API key
3. Add the key to your environment variables

## 🔧 Environment Configuration

### Backend Environment Variables
Create `backend/.env` based on `backend/.env.example`:

```bash
# REQUIRED
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
DATABASE_URL=sqlite:///./neuro_tutor.db

# OPTIONAL (Development)
DEBUG=True
CORS_ORIGINS=http://localhost:5173,http://localhost:5180
```

### Frontend Environment Variables
The frontend automatically reads `VITE_API_URL` from the environment:
- Default: `http://localhost:8000` (local development)
- Docker: Automatically set to `http://localhost:8000`

## 🐳 Docker Deployment

### Building and Running
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Service Architecture
- **Backend Service**: Python FastAPI app on port 8000
- **Frontend Service**: Built React app served on port 5173
- **Database**: SQLite volume persisted in Docker volume
- **Health Checks**: Both services include health monitoring

### Production Considerations
1. **Database**: For production, consider PostgreSQL:
   ```yaml
   environment:
     - DATABASE_URL=postgresql://user:pass@postgres:5432/neuro_tutor
   ```

2. **Environment**: Set production values in `backend/.env`:
   ```bash
   DEBUG=False
   OPENROUTER_API_KEY=your-production-key
   ```

3. **Security**: Never commit `.env` files to version control

## 🛠️ Local Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
python -m pytest

# Test specific endpoint
curl http://localhost:8000/health
```

### Frontend Development
```bash
cd socratic-tutor-frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📊 API Endpoints

### Health & Status
- `GET /health` - Service health check
- `GET /docs` - Interactive API documentation

### Chat API
- `POST /api/chat/` - Send message and get AI response
- `GET /api/chat/sessions` - List all chat sessions
- `GET /api/chat/sessions/{id}/messages` - Get session history
- `DELETE /api/chat/sessions/{id}` - Delete session

### Example API Usage
```bash
# Start a new chat
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "preferences": {"verbosity_level": 3}
  }'

# Get sessions
curl "http://localhost:8000/api/chat/sessions"
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Ensure ports 8000 and 5173 are available
   - Modify `docker-compose.yml` ports if needed

2. **API Key Errors**
   - Verify OpenRouter key is valid and active
   - Check `backend/.env` file permissions

3. **Database Issues**
   - For Docker: Check volume permissions
   - For local: Ensure write permissions for SQLite file

4. **Frontend Connection**
   - Verify `VITE_API_URL` environment variable
   - Check CORS settings in backend configuration

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:5173

# Docker service status
docker-compose ps
```

## 📈 Monitoring & Logs

### Docker Logs
```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# View recent logs
docker-compose logs --tail=100
```

### Application Logs
- Backend logs include request details and errors
- Frontend shows build warnings and development info
- Database operations are logged at appropriate levels

## 🔒 Security Notes

1. **API Keys**: Never commit to version control
2. **Environment**: Use different keys for dev/prod
3. **CORS**: Configure proper origins for production
4. **Database**: Use connection pooling for production
5. **HTTPS**: Enable SSL in production environments

## 📁 File Structure

```
neuro-tutor/
├── backend/
│   ├── app/                    # FastAPI application
│   ├── Dockerfile               # Backend container definition
│   ├── requirements.txt         # Python dependencies
│   └── .env.example           # Environment template
├── socratic-tutor-frontend/
│   ├── src/                    # React application
│   ├── Dockerfile             # Frontend container definition
│   └── package.json           # Node.js dependencies
├── docker-compose.yml           # Service orchestration
└── DEPLOYMENT.md             # This guide
```

## 🚀 Production Deployment

### Cloud Platforms
1. **Configure Environment Variables** in your hosting platform
2. **Build Images**: `docker-compose build`
3. **Push to Registry**: Push to container registry
4. **Deploy**: Use platform's container deployment

### Environment Variables for Production
```bash
# Required
OPENROUTER_API_KEY=your-production-api-key
DATABASE_URL=postgresql://user:password@host:port/dbname

# Recommended
DEBUG=False
CORS_ORIGINS=https://yourdomain.com
DEFAULT_MODEL=qwen2.5:72b-instruct
```

## 📞 Support

For issues with:
- **OpenRouter API**: Check [OpenRouter Docs](https://openrouter.ai/docs)
- **Docker**: Review [Docker Compose Docs](https://docs.docker.com/compose/)
- **Application**: Check logs and ensure environment is properly configured

---

*Last Updated: 2025-11-27*
*Version: 1.0.0*
