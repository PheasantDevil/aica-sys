"""
AICA-SyS Backend Main Application
AI-driven Content Curation & Automated Sales System
"""

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
# Import audit middleware
from middleware.audit_middleware import AuditMiddleware
# Import monitoring middleware
from middleware.monitoring_middleware import MonitoringMiddleware
# Import performance middleware
from middleware.performance_middleware import performance_metrics
# Import security middleware
from security.security_headers import SecurityHeadersMiddleware

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

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Add audit middleware
app.add_middleware(AuditMiddleware)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

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
    return performance_metrics.get_stats()

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with performance metrics"""
    health_status = performance_metrics.get_stats()
    return health_status

# Import routers
from routers import (ai_router, analysis_router, audit_router, auth_router,
                     collection_router, content_management_router,
                     content_router, monitoring_router, reports_router,
                     subscription_router, user_router)
from routers.optimized_content_router import router as optimized_content_router
from routers.content_quality_router import router as content_quality_router
from routers.engagement_router import router as engagement_router

# Include routers
app.include_router(content_router)
app.include_router(collection_router)
app.include_router(analysis_router)
app.include_router(ai_router.router)
app.include_router(auth_router.router)
app.include_router(subscription_router.router)
app.include_router(reports_router.router)
app.include_router(user_router.router)
app.include_router(content_management_router.router)
app.include_router(monitoring_router.router)
app.include_router(audit_router.router)
app.include_router(optimized_content_router)
app.include_router(content_quality_router)
app.include_router(engagement_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
