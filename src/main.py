"""
Task Manager API - Main Application Entry Point

This module initializes the FastAPI application and configures
all routes, middleware, and dependencies.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router
from src.api.comments import router as comments_router
from src.services.database import init_db

app = FastAPI(
    title="Task Manager API",
    description="A simple task management REST API",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(comments_router, prefix="/api/comments", tags=["Comments"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup."""
    await init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "1.0.0"}
