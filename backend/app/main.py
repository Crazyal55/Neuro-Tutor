"""
Main FastAPI application for Neuro Tutor backend.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings, get_cors_config
from app.core.middleware import RequestLoggingMiddleware
from app.core.migrations import run_migrations
from app.core.rate_limit import limiter
from app.core.vector_db import ensure_collection
from app.api import chat, subjects

from app.models import chat as chat_models  # noqa: F401 — register SQLAlchemy models
from app.models import subjects as subject_models  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    if os.getenv("TESTING") != "1" and settings.auto_migrate:
        run_migrations()
    if os.getenv("TESTING") != "1":
        ensure_collection()
    logger.info("%s v%s starting", settings.app_name, settings.app_version)
    yield
    logger.info("%s shutting down", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI tutor backend specialized for neurodivergent students",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.add_middleware(SlowAPIMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSMiddleware, **get_cors_config())

app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(subjects.router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI tutor backend specialized for neurodivergent students",
        "docs_url": "/docs",
        "health": "OK",
        "auth": "none — single-user local deployment",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
