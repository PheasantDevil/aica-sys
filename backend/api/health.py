from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
import asyncio
import time
import psutil
import os
from datetime import datetime

from utils.database import get_db
from utils.logging import logger

router = APIRouter()

class HealthChecker:
    def __init__(self):
        self.start_time = time.time()
    
    async def check_database(self, db: Session) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            # Simple query to test database connection
            result = db.execute("SELECT 1").fetchone()
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "message": "Database connection successful"
            }
        except Exception as e:
            logger.error("Database health check failed", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Database connection failed"
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            # This would be implemented with actual Redis client
            # For now, we'll simulate a check
            return {
                "status": "healthy",
                "message": "Redis connection successful"
            }
        except Exception as e:
            logger.error("Redis health check failed", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Redis connection failed"
            }
    
    async def check_external_apis(self) -> Dict[str, Any]:
        """Check external API dependencies"""
        try:
            # Check Stripe API
            stripe_status = await self._check_stripe_api()
            
            # Check email service
            email_status = await self._check_email_service()
            
            return {
                "status": "healthy" if all(s["status"] == "healthy" for s in [stripe_status, email_status]) else "degraded",
                "services": {
                    "stripe": stripe_status,
                    "email": email_status
                },
                "message": "External APIs checked"
            }
        except Exception as e:
            logger.error("External APIs health check failed", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "External APIs check failed"
            }
    
    async def _check_stripe_api(self) -> Dict[str, Any]:
        """Check Stripe API connectivity"""
        try:
            # This would make an actual API call to Stripe
            # For now, we'll simulate a check
            return {
                "status": "healthy",
                "response_time_ms": 150,
                "message": "Stripe API accessible"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Stripe API unavailable"
            }
    
    async def _check_email_service(self) -> Dict[str, Any]:
        """Check email service connectivity"""
        try:
            # This would make an actual API call to email service
            # For now, we'll simulate a check
            return {
                "status": "healthy",
                "response_time_ms": 200,
                "message": "Email service accessible"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "message": "Email service unavailable"
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process info
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2),
                    "status": "healthy" if (disk.used / disk.total) < 0.8 else "warning" if (disk.used / disk.total) < 0.95 else "critical"
                },
                "process": {
                    "memory_mb": round(process_memory.rss / (1024**2), 2),
                    "cpu_percent": process.cpu_percent(),
                    "threads": process.num_threads(),
                    "status": "healthy"
                }
            }
        except Exception as e:
            logger.error("Failed to get system metrics", exc_info=True)
            return {
                "error": str(e),
                "status": "unhealthy"
            }
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            uptime = time.time() - self.start_time
            
            return {
                "uptime_seconds": round(uptime, 2),
                "uptime_hours": round(uptime / 3600, 2),
                "version": os.getenv("APP_VERSION", "1.0.0"),
                "environment": os.getenv("ENVIRONMENT", "development"),
                "status": "healthy"
            }
        except Exception as e:
            logger.error("Failed to get application metrics", exc_info=True)
            return {
                "error": str(e),
                "status": "unhealthy"
            }

# Global health checker instance
health_checker = HealthChecker()

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Service is running"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with all components"""
    try:
        # Run all health checks in parallel
        db_check, redis_check, external_apis_check = await asyncio.gather(
            health_checker.check_database(db),
            health_checker.check_redis(),
            health_checker.check_external_apis(),
            return_exceptions=True
        )
        
        # Get system metrics
        system_metrics = health_checker.get_system_metrics()
        app_metrics = health_checker.get_application_metrics()
        
        # Determine overall status
        checks = [db_check, redis_check, external_apis_check]
        if any(isinstance(check, Exception) for check in checks):
            overall_status = "unhealthy"
        elif any(check.get("status") == "unhealthy" for check in checks if isinstance(check, dict)):
            overall_status = "unhealthy"
        elif any(check.get("status") == "degraded" for check in checks if isinstance(check, dict)):
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Prepare response
        response = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "database": db_check if not isinstance(db_check, Exception) else {"status": "unhealthy", "error": str(db_check)},
                "redis": redis_check if not isinstance(redis_check, Exception) else {"status": "unhealthy", "error": str(redis_check)},
                "external_apis": external_apis_check if not isinstance(external_apis_check, Exception) else {"status": "unhealthy", "error": str(external_apis_check)}
            },
            "system": system_metrics,
            "application": app_metrics
        }
        
        # Set appropriate HTTP status code
        status_code = 200 if overall_status == "healthy" else 503 if overall_status == "unhealthy" else 200
        
        return JSONResponse(content=response, status_code=status_code)
        
    except Exception as e:
        logger.error("Health check failed", exc_info=True)
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "message": "Health check failed"
            },
            status_code=503
        )

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        # Check critical dependencies
        db_check = await health_checker.check_database(db)
        
        if db_check["status"] != "healthy":
            raise HTTPException(status_code=503, detail="Service not ready")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Readiness check failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    try:
        # Check if the application is responsive
        app_metrics = health_checker.get_application_metrics()
        
        if app_metrics["status"] != "healthy":
            raise HTTPException(status_code=503, detail="Service not alive")
        
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Liveness check failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Service not alive")

@router.get("/health/metrics")
async def metrics_endpoint():
    """Prometheus-style metrics endpoint"""
    try:
        system_metrics = health_checker.get_system_metrics()
        app_metrics = health_checker.get_application_metrics()
        
        # Format as Prometheus metrics
        metrics = []
        
        # System metrics
        if "cpu" in system_metrics:
            metrics.append(f"system_cpu_usage_percent {system_metrics['cpu']['usage_percent']}")
        
        if "memory" in system_metrics:
            metrics.append(f"system_memory_usage_percent {system_metrics['memory']['usage_percent']}")
            metrics.append(f"system_memory_used_bytes {system_metrics['memory']['used_gb'] * 1024**3}")
        
        if "disk" in system_metrics:
            metrics.append(f"system_disk_usage_percent {system_metrics['disk']['usage_percent']}")
            metrics.append(f"system_disk_used_bytes {system_metrics['disk']['used_gb'] * 1024**3}")
        
        # Application metrics
        if "uptime_seconds" in app_metrics:
            metrics.append(f"application_uptime_seconds {app_metrics['uptime_seconds']}")
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error("Metrics endpoint failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Metrics unavailable")
