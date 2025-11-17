"""
Enhanced Authentication and Authorization Middleware
Provides comprehensive security for API endpoints
"""

import hashlib
import logging
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Dict, List, Optional

import bcrypt
import jwt
from database import get_db
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from models.user import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = "your-secret-key"  # Should be from environment
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security schemes
security = HTTPBearer()


class SecurityConfig:
    """Security configuration class"""

    def __init__(self):
        self.jwt_secret = JWT_SECRET_KEY
        self.jwt_algorithm = JWT_ALGORITHM
        self.access_token_expire = ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = REFRESH_TOKEN_EXPIRE_DAYS
        self.rate_limit_requests = 100
        self.rate_limit_window = 3600  # 1 hour

    def get_jwt_secret(self) -> str:
        """Get JWT secret from environment"""
        import os

        return os.getenv("JWT_SECRET_KEY", self.jwt_secret)

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, List[float]] = {}


class AuthenticationError(Exception):
    """Custom authentication error"""

    pass


class AuthorizationError(Exception):
    """Custom authorization error"""

    pass


class RateLimitError(Exception):
    """Custom rate limit error"""

    pass


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except PyJWTError:
        raise AuthenticationError("Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = verify_token(token)

        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise AuthenticationError("User not found")

        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def require_roles(required_roles: List[str]):
    """Decorator to require specific roles"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_permissions(required_permissions: List[str]):
    """Decorator to require specific permissions"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has required permissions
            user_permissions = get_user_permissions(current_user)
            if not all(perm in user_permissions for perm in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_user_permissions(user: User) -> List[str]:
    """Get user permissions based on role"""
    permissions = {
        "admin": [
            "read:all",
            "write:all",
            "delete:all",
            "manage:users",
            "manage:content",
            "manage:system",
        ],
        "editor": ["read:all", "write:content", "delete:own", "manage:content"],
        "user": ["read:own", "write:own", "delete:own"],
    }
    return permissions.get(user.role, [])


def check_rate_limit(request: Request, user_id: Optional[str] = None) -> bool:
    """Check rate limit for user or IP"""
    config = SecurityConfig()
    identifier = user_id or request.client.host

    now = time.time()
    window_start = now - config.rate_limit_window

    # Clean old entries
    if identifier in rate_limit_storage:
        rate_limit_storage[identifier] = [
            timestamp
            for timestamp in rate_limit_storage[identifier]
            if timestamp > window_start
        ]
    else:
        rate_limit_storage[identifier] = []

    # Check if limit exceeded
    if len(rate_limit_storage[identifier]) >= config.rate_limit_requests:
        return False

    # Add current request
    rate_limit_storage[identifier].append(now)
    return True


def rate_limit_dependency():
    """Dependency for rate limiting"""

    def check_rate_limit_func(
        request: Request, current_user: User = Depends(get_current_user)
    ):
        if not check_rate_limit(request, str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        return current_user

    return check_rate_limit_func


def validate_input_data(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate input data for required fields"""
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    return True


def sanitize_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize input data to prevent injection attacks"""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized[key] = value.strip().replace("<", "&lt;").replace(">", "&gt;")
        else:
            sanitized[key] = value
    return sanitized


def log_security_event(
    event_type: str, user_id: Optional[str], details: Dict[str, Any]
):
    """Log security events for monitoring"""
    logger.warning(
        f"Security Event: {event_type}",
        extra={
            "user_id": user_id,
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Security decorators for common use cases
def require_auth(func):
    """Require authentication decorator"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        if "current_user" not in kwargs:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
        return await func(*args, **kwargs)

    return wrapper


def require_admin(func):
    """Require admin role decorator"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if not current_user or current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
            )
        return await func(*args, **kwargs)

    return wrapper


def require_editor(func):
    """Require editor role decorator"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get("current_user")
        if not current_user or current_user.role not in ["admin", "editor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Editor access required"
            )
        return await func(*args, **kwargs)

    return wrapper
