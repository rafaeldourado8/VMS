"""
FastAPI Streaming Service - Main Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events."""
    logger.info("🚀 Starting Streaming Service...")
    yield
    logger.info("🛑 Shutting down Streaming Service...")


# Create FastAPI app
app = FastAPI(
    title="GT Vision Streaming Service",
    description="Real-time video streaming service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "GT Vision Streaming Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "streaming-service",
        "version": "1.0.0",
        "active_streams": 0
    }


# Import routes
try:
    from api.routes import streams
    app.include_router(streams.router, prefix="/api/v1", tags=["streams"])
    logger.info("✅ Streams routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Streams routes not loaded: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )