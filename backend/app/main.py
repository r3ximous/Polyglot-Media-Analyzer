from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging

from .core.config import settings
from .core.database import engine, Base
from .api import api_router
from .utils import setup_logging, ensure_directories
from .services.elasticsearch_service import ElasticSearchService

# Setup logging and directories
setup_logging()
ensure_directories()

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Initialize ElasticSearch index
        es_service = ElasticSearchService()
        await es_service.create_index()
        
        logger.info("Application startup completed")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        # Close ElasticSearch connection
        es_service = ElasticSearchService()
        await es_service.close()
        
        logger.info("Application shutdown completed")
        
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Polyglot Media Analyzer",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_url": settings.API_V1_STR
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )