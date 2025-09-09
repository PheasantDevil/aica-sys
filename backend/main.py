"""
AICA-SyS Backend Main Application
AI-driven Content Curation & Automated Sales System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AICA-SyS API",
    description="AI-driven Content Curation & Automated Sales System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://aica-sys.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"]
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

# Import routers (will be created in future phases)
# from app.routers import content, auth, subscription

# app.include_router(content.router, prefix="/api/content", tags=["content"])
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )
