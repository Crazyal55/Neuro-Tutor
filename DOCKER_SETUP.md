# Docker Setup Guide for Neuro-Tutor

## Overview
This guide explains how to build and run the Neuro-Tutor application using Docker containers.

## Prerequisites
- Docker installed on your system
- Docker Compose installed
- OpenRouter API key

## Quick Start

### 1. Environment Configuration
Copy the Docker environment template and configure your API key:

```bash
cp .env.docker.example .env
```

Edit `.env` file with your actual OpenRouter API key:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
DEFAULT_MODEL=openai/gpt-3.5-turbo
DATABASE_URL=sqlite:///./data/neuro_tutor.db
```

### 2. Build and Run
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 3. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health Check: http://localhost:8000/health

## Services

### Backend Service
- **Port**: 8000
- **Health Check**: Every 30 seconds
- **Environment Variables**:
  - `OPENROUTER_API_KEY`: Your OpenRouter API key
  - `DEFAULT_MODEL`: AI model to use (default: openai/gpt-3.5-turbo)
  - `DATABASE_URL`: SQLite database path

### Frontend Service
- **Port**: 5173
- **Health Check**: Every 30 seconds
- **Environment Variables**:
  - `VITE_API_URL`: Backend API URL (automatically set to http://backend:8000/api)
- **Dependencies**: Waits for backend to be healthy

## Docker Configuration Details

### Backend Dockerfile Features
- Python 3.11 slim base image
- Installs required system dependencies (gcc, curl)
- Multi-stage build for better caching
- Non-root user for security
- Health check endpoint
- Proper port exposure

### Frontend Dockerfile Features
- Node.js 20 LTS Alpine base image
- Optimized build layers
- Lightweight server for production
- Health check endpoint
- Proper port exposure

### Docker Compose Features
- Service dependencies (frontend waits for backend)
- Volume mounts for development
- Health checks for both services
- Automatic restart policies
- Proper network configuration

## Development vs Production

### Development Mode
```bash
# With live reloading
docker-compose up --build
```

### Production Mode
```bash
# Without volume mounts (use containerized code)
docker-compose -f docker-compose.prod.yml up --build -d
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `.env` file exists in project root
   - Check that `OPENROUTER_API_KEY` is set correctly
   - Verify environment variable spelling

2. **Build Failures**
   - Check Docker is running: `docker --version`
   - Clear build cache: `docker system prune -f`
   - Check system dependencies in Dockerfiles

3. **Connection Issues**
   - Verify backend health check: `curl http://localhost:8000/health`
   - Check container logs: `docker-compose logs backend`
   - Ensure ports are not already in use

4. **Frontend Can't Reach Backend**
   - Check Docker network: `docker network ls`
   - Verify service names in docker-compose.yml
   - Check CORS settings

### Useful Commands
```bash
# View logs
docker-compose logs -f

# Check container status
docker-compose ps

# Restart services
docker-compose restart

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose up --build backend
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|-----------|----------|----------|-------------|
| OPENROUTER_API_KEY | Yes | YOUR_OPENROUTER_API_KEY_HERE | OpenRouter API key |
| DEFAULT_MODEL | No | openai/gpt-3.5-turbo | AI model to use |
| DATABASE_URL | No | sqlite:///./data/neuro_tutor.db | Database connection |
| VITE_API_URL | No | http://backend:8000/api | Frontend API URL |
| DEBUG | No | false | Enable debug mode |
| CORS_ORIGINS | No | http://localhost:5173,http://localhost:3000 | Allowed origins |

## Security Notes

- API keys are loaded from environment variables (not hardcoded)
- Non-root user for backend container
- Health checks use minimal endpoints
- Volume mounts are for development only
- Consider using secrets management in production

## Performance Optimizations

- Docker layer caching in Dockerfiles
- Separate build and run stages
- Health checks with appropriate intervals
- Proper resource limits can be added
- Database volume persistence
