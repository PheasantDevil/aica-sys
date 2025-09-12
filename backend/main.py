"""
AICA-SyS Backend Main Application
AI-driven Content Curation & Automated Sales System
"""

import os
import logging

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Import performance middleware
from middleware.performance_middleware import PerformanceMiddleware, performance_monitor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AICA-SyS API",
    description="AI-driven Content Curation & Automated Sales System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add performance monitoring middleware (first)
app.add_middleware(PerformanceMiddleware, enable_logging=True)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://aica-sys.vercel.app",
        "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.supabase.co"]
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AICA-SyS API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/metrics")
async def get_metrics():
    """Performance metrics endpoint"""
    return performance_monitor.get_metrics()

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with performance metrics"""
    health_status = performance_monitor.get_health_status()
    return health_status

# Import routers
from routers import (ai_router, analysis_router, collection_router,
                     content_router)

# Include routers
app.include_router(content_router)
app.include_router(collection_router)
app.include_router(analysis_router)
app.include_router(ai_router.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
