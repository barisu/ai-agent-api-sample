import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import documents, health, query
from src.config import settings
from src.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database tables
    - Shutdown: Cleanup resources (if needed)
    """
    # Startup
    logger.info("Starting RAG API application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down RAG API application...")


# Create FastAPI application
app = FastAPI(
    title="RAG API",
    description="Retrieval-Augmented Generation API with LangChain, LangGraph, and PostgreSQL pgvector",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(documents.router)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "RAG API",
        "version": "0.1.0",
        "description": "Retrieval-Augmented Generation API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
