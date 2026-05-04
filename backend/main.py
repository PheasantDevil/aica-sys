"""
AICA-SyS Backend Main Application
AI-driven Content Curation & Automated Sales System
"""

import asyncio
import logging
import os
from contextlib import suppress

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
content_sync_task: asyncio.Task | None = None

# Create FastAPI app
app = FastAPI(
    title="AICA-SyS API",
    description="AI-driven Content Curation & Automated Sales System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
        "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "*.vercel.app",
        "*.supabase.co",
        "*.onrender.com",
    ],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AICA-SyS API", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@app.get("/metrics")
async def get_metrics():
    """Performance metrics endpoint"""
    return performance_metrics.get_stats()


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with performance metrics"""
    health_status = performance_metrics.get_stats()
    return health_status


async def _periodic_content_sync():
    from database import SessionLocal
    from services.content_sync_service import get_content_sync_service

    interval_seconds = int(os.getenv("CONTENT_SYNC_INTERVAL_SECONDS", "600"))
    sync_service = get_content_sync_service()

    while True:
        db = SessionLocal()
        try:
            stats = sync_service.sync_published_content(db)
            if stats["scanned"] > 0:
                logger.info(
                    "[content-sync][startup-task] scanned=%s article=%s newsletter=%s trend=%s",
                    stats["scanned"],
                    stats["article_upserts"],
                    stats["newsletter_upserts"],
                    stats["trend_upserts"],
                )
        except Exception:
            logger.exception("Periodic content sync failed")
        finally:
            db.close()

        await asyncio.sleep(interval_seconds)


@app.on_event("startup")
async def start_background_content_sync():
    global content_sync_task
    if os.getenv("ENABLE_CONTENT_SYNC", "true").lower() != "true":
        logger.info("Background content sync disabled by ENABLE_CONTENT_SYNC")
        return

    if content_sync_task and not content_sync_task.done():
        return

    content_sync_task = asyncio.create_task(_periodic_content_sync())
    logger.info("Background content sync task started")


@app.on_event("shutdown")
async def stop_background_content_sync():
    global content_sync_task
    if not content_sync_task:
        return

    content_sync_task.cancel()
    with suppress(asyncio.CancelledError):
        await content_sync_task
    content_sync_task = None
    logger.info("Background content sync task stopped")


# Import routers
from routers import (
    ai_router,
    analysis_router,
    audit_router,
    auth_router,
    collection_router,
    content_management_router,
    content_router,
    monitoring_router,
    reports_router,
    subscription_router,
    user_router,
)
from routers.affiliate_router import router as affiliate_router
from routers.analytics_router import router as analytics_router
from routers.content_quality_router import router as content_quality_router
from routers.engagement_router import router as engagement_router
from routers.optimized_content_router import router as optimized_content_router
from routers.subscription_enhanced_router import router as subscription_enhanced_router

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
app.include_router(subscription_enhanced_router)
app.include_router(affiliate_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
    )
