"""
Main FastAPI application for PockEat API.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import uvicorn
from dotenv import load_dotenv
import traceback
import psutil
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PockEat API",
    description="API for food and exercise analysis using Google's Gemini models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import API routers - must be after app creation
from api.routes import router as api_router

# Register routers
app.include_router(api_router, prefix="/api")

# Root endpoint serves as a health check
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint serving as a health check."""
    return {
        "status": "healthy",
        "message": "PockEat API is running",
        "version": app.version
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check endpoint."""
    # Check memory usage
    memory = psutil.virtual_memory()
    
    # Check if Google API key is set
    api_key_set = os.getenv("GOOGLE_API_KEY") is not None
    
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": time.time(),
        "system": {
            "memory_usage_percent": memory.percent,
            "cpu_usage_percent": psutil.cpu_percent(interval=0.1)
        },
        "services": {
            "gemini": "available" if api_key_set else "unavailable"
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Debug environment variables endpoint
@app.get("/debug-env", tags=["Debug"])
async def debug_env():
    """Debug endpoint for environment variables."""
    return {
        "has_key": bool(os.getenv("GOOGLE_API_KEY")),
        "env_vars": list(os.environ.keys())
    }

# Exception handler for requests
@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    """Middleware for handling exceptions in requests."""
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a structured error response
        return HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

# Run the application when executed directly
if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"Starting PockEat API on {host}:{port}")
    
    # Run the FastAPI application with uvicorn
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    ) 