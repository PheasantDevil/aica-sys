import structlog
import logging
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
from pathlib import Path

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Logger:
    def __init__(self):
        self.is_development = os.getenv("ENVIRONMENT", "development") == "development"
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Create logger
        logger = structlog.get_logger()
        
        # Configure file handlers
        if not self.is_development:
            self._setup_file_handlers(logger)
        
        return logger
    
    def _setup_file_handlers(self, logger):
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Error log handler
        error_handler = logging.handlers.RotatingFileHandler(
            "logs/error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Application log handler
        app_handler = logging.handlers.RotatingFileHandler(
            "logs/app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        app_handler.setLevel(logging.INFO)
        app_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Security log handler
        security_handler = logging.handlers.RotatingFileHandler(
            "logs/security.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=10
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        
        # Add handlers to logger
        logger.addHandler(error_handler)
        logger.addHandler(app_handler)
        logger.addHandler(security_handler)
    
    def _log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        log_data = {
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if context:
            log_data.update(context)
        
        log_data.update(kwargs)
        
        if level == LogLevel.DEBUG:
            self.logger.debug(message, **log_data)
        elif level == LogLevel.INFO:
            self.logger.info(message, **log_data)
        elif level == LogLevel.WARNING:
            self.logger.warning(message, **log_data)
        elif level == LogLevel.ERROR:
            self.logger.error(message, **log_data)
        elif level == LogLevel.CRITICAL:
            self.logger.critical(message, **log_data)
    
    # Public logging methods
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(LogLevel.DEBUG, message, context, **kwargs)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(LogLevel.INFO, message, context, **kwargs)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(LogLevel.WARNING, message, context, **kwargs)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(LogLevel.ERROR, message, context, **kwargs)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log(LogLevel.CRITICAL, message, context, **kwargs)
    
    # Specialized logging methods
    def api_request(self, method: str, path: str, status_code: int, duration: float, 
                   user_id: Optional[str] = None, ip_address: Optional[str] = None, **kwargs):
        self.info(f"API Request: {method} {path}", {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "user_id": user_id,
            "ip_address": ip_address,
            "component": "api",
            **kwargs
        })
    
    def user_action(self, action: str, user_id: str, **kwargs):
        self.info(f"User Action: {action}", {
            "action": action,
            "user_id": user_id,
            "component": "user-action",
            **kwargs
        })
    
    def security_event(self, event: str, severity: str = "medium", **kwargs):
        level = LogLevel.WARNING if severity == "high" else LogLevel.INFO
        self._log(level, f"Security Event: {event}", {
            "event": event,
            "severity": severity,
            "component": "security",
            **kwargs
        })
    
    def business_event(self, event: str, **kwargs):
        self.info(f"Business Event: {event}", {
            "event": event,
            "component": "business",
            **kwargs
        })
    
    def performance(self, metric: str, value: float, **kwargs):
        self.info(f"Performance: {metric} = {value}", {
            "metric": metric,
            "value": value,
            "component": "performance",
            **kwargs
        })
    
    def database_operation(self, operation: str, table: str, duration: float, **kwargs):
        self.info(f"Database Operation: {operation} on {table}", {
            "operation": operation,
            "table": table,
            "duration_ms": duration * 1000,
            "component": "database",
            **kwargs
        })
    
    def external_api_call(self, service: str, endpoint: str, status_code: int, duration: float, **kwargs):
        self.info(f"External API Call: {service} {endpoint}", {
            "service": service,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration * 1000,
            "component": "external-api",
            **kwargs
        })
    
    def error_with_exception(self, message: str, exception: Exception, **kwargs):
        self.error(message, {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "component": "exception",
            **kwargs
        }, exc_info=True)

# Global logger instance
logger = Logger()

# Convenience functions
def log_api_request(method: str, path: str, status_code: int, duration: float, **kwargs):
    logger.api_request(method, path, status_code, duration, **kwargs)

def log_user_action(action: str, user_id: str, **kwargs):
    logger.user_action(action, user_id, **kwargs)

def log_security_event(event: str, severity: str = "medium", **kwargs):
    logger.security_event(event, severity, **kwargs)

def log_business_event(event: str, **kwargs):
    logger.business_event(event, **kwargs)

def log_performance(metric: str, value: float, **kwargs):
    logger.performance(metric, value, **kwargs)

def log_database_operation(operation: str, table: str, duration: float, **kwargs):
    logger.database_operation(operation, table, duration, **kwargs)

def log_external_api_call(service: str, endpoint: str, status_code: int, duration: float, **kwargs):
    logger.external_api_call(service, endpoint, status_code, duration, **kwargs)

def log_error_with_exception(message: str, exception: Exception, **kwargs):
    logger.error_with_exception(message, exception, **kwargs)
