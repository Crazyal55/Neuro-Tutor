"""
Main FastAPI application for Neuro Tutor backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings, get_cors_config
from app.api import chat

# Import models to ensure they're registered with SQLAlchemy
from app.models import chat as chat_models

# Import database and create tables after models are loaded
from app.core.db import create_tables
create_tables()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"🧠 {settings.app_name} v{settings.app_version} starting up...")
    print(f"🔧 Debug mode: {settings.debug}")
    yield
    # Shutdown
    print("🧠 Neuro Tutor API shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI tutor backend specialized for neurodivergent students",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **get_cors_config()
)

# Include routers
app.include_router(chat.router, prefix=settings.api_prefix)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI tutor backend specialized for neurodivergent students",
        "docs_url": "/docs",
        "health": "OK"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    print(f"❌ Unhandled exception: {exc}")
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
