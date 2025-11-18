import html
import logging
import re
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import bleach
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class InputValidator:
    def __init__(self):
        # Common patterns
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        self.username_pattern = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        self.password_pattern = re.compile(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        )
        self.url_pattern = re.compile(
            r"^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$"
        )

        # Allowed HTML tags for rich text
        self.allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "u",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "blockquote",
            "code",
            "pre",
            "a",
            "img",
        ]

        # Allowed HTML attributes
        self.allowed_attributes = {
            "a": ["href", "title", "target"],
            "img": ["src", "alt", "title", "width", "height"],
            "code": ["class"],
            "pre": ["class"],
        }

    def sanitize_string(self, value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")

        # Remove null bytes and control characters
        value = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", value)

        # Trim whitespace
        value = value.strip()

        # Check length
        if len(value) > max_length:
            raise ValueError(f"String too long. Maximum length: {max_length}")

        # HTML escape
        value = html.escape(value, quote=True)

        return value

    def sanitize_html(self, value: str, max_length: int = 10000) -> str:
        """Sanitize HTML input"""
        if not isinstance(value, str):
            raise ValueError("Input must be a string")

        # Check length
        if len(value) > max_length:
            raise ValueError(f"HTML too long. Maximum length: {max_length}")

        # Use bleach to sanitize HTML
        cleaned = bleach.clean(
            value,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True,
        )

        return cleaned

    def validate_email(self, email: str) -> str:
        """Validate email address"""
        if not isinstance(email, str):
            raise ValueError("Email must be a string")

        email = email.strip().lower()

        if not self.email_pattern.match(email):
            raise ValueError("Invalid email format")

        if len(email) > 254:  # RFC 5321 limit
            raise ValueError("Email too long")

        return email

    def validate_username(self, username: str) -> str:
        """Validate username"""
        if not isinstance(username, str):
            raise ValueError("Username must be a string")

        username = username.strip()

        if not self.username_pattern.match(username):
            raise ValueError(
                "Username must be 3-20 characters long and contain only "
                "letters, numbers, underscores, and hyphens"
            )

        return username

    def validate_password(self, password: str) -> str:
        """Validate password strength"""
        if not isinstance(password, str):
            raise ValueError("Password must be a string")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(password) > 128:
            raise ValueError("Password too long")

        if not self.password_pattern.match(password):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character"
            )

        return password

    def validate_url(self, url: str) -> str:
        """Validate URL"""
        if not isinstance(url, str):
            raise ValueError("URL must be a string")

        url = url.strip()

        if not self.url_pattern.match(url):
            raise ValueError("Invalid URL format")

        # Parse URL to check for suspicious patterns
        parsed = urlparse(url)

        # Check for suspicious schemes
        if parsed.scheme not in ["http", "https"]:
            raise ValueError("URL must use HTTP or HTTPS protocol")

        # Check for suspicious domains
        suspicious_domains = ["localhost", "127.0.0.1", "0.0.0.0"]
        if parsed.hostname in suspicious_domains:
            raise ValueError("URL cannot point to localhost")

        return url

    def validate_json(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JSON data against schema"""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        validated_data = {}

        for field, rules in schema.items():
            if field not in data:
                if rules.get("required", False):
                    raise ValueError(f"Required field '{field}' is missing")
                continue

            value = data[field]
            field_type = rules.get("type", str)

            # Type validation
            if not isinstance(value, field_type):
                try:
                    value = field_type(value)
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Field '{field}' must be of type {field_type.__name__}"
                    )

            # String-specific validations
            if field_type == str:
                max_length = rules.get("max_length", 1000)
                min_length = rules.get("min_length", 0)

                if len(value) < min_length:
                    raise ValueError(
                        f"Field '{field}' must be at least {min_length} characters long"
                    )

                if len(value) > max_length:
                    raise ValueError(
                        f"Field '{field}' must be no more than {max_length} characters long"
                    )

                # Sanitize string
                if rules.get("sanitize", True):
                    value = self.sanitize_string(value, max_length)

            # Email validation
            if rules.get("format") == "email":
                value = self.validate_email(value)

            # URL validation
            if rules.get("format") == "url":
                value = self.validate_url(value)

            # HTML validation
            if rules.get("format") == "html":
                value = self.sanitize_html(value, rules.get("max_length", 10000))

            validated_data[field] = value

        return validated_data

    def validate_pagination(self, page: int, per_page: int) -> tuple[int, int]:
        """Validate pagination parameters"""
        if not isinstance(page, int) or page < 1:
            raise ValueError("Page must be a positive integer")

        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            raise ValueError("Per page must be between 1 and 100")

        return page, per_page

    def validate_sort_params(self, sort_by: str, sort_order: str) -> tuple[str, str]:
        """Validate sort parameters"""
        if not isinstance(sort_by, str):
            raise ValueError("Sort by must be a string")

        if not isinstance(sort_order, str):
            raise ValueError("Sort order must be a string")

        sort_by = sort_by.strip().lower()
        sort_order = sort_order.strip().lower()

        if sort_order not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")

        return sort_by, sort_order


# Global input validator
input_validator = InputValidator()


# Pydantic models for common validations
class EmailInput(BaseModel):
    email: str = Field(..., min_length=1, max_length=254)

    @validator("email")
    def validate_email(cls, v):
        return input_validator.validate_email(v)


class UsernameInput(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)

    @validator("username")
    def validate_username(cls, v):
        return input_validator.validate_username(v)


class PasswordInput(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)

    @validator("password")
    def validate_password(cls, v):
        return input_validator.validate_password(v)


class URLInput(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)

    @validator("url")
    def validate_url(cls, v):
        return input_validator.validate_url(v)


class PaginationInput(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

    @validator("page", "per_page")
    def validate_pagination(cls, v):
        if not isinstance(v, int) or v < 1:
            raise ValueError("Must be a positive integer")
        return v


class SortInput(BaseModel):
    sort_by: str = Field("created_at", min_length=1, max_length=50)
    sort_order: str = Field("desc", regex="^(asc|desc)$")


# Input sanitization decorator
def sanitize_input(schema: Dict[str, Any]):
    """Decorator for input sanitization"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find request data in arguments
            request_data = None
            for arg in args:
                if isinstance(arg, dict):
                    request_data = arg
                    break

            if request_data:
                try:
                    # Validate and sanitize input
                    validated_data = input_validator.validate_json(request_data, schema)

                    # Replace original data with validated data
                    for i, arg in enumerate(args):
                        if isinstance(arg, dict) and arg is request_data:
                            args = list(args)
                            args[i] = validated_data
                            break

                    return await func(*args, **kwargs)
                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Common validation schemas
VALIDATION_SCHEMAS = {
    "user_registration": {
        "email": {"type": str, "format": "email", "required": True},
        "username": {"type": str, "min_length": 3, "max_length": 20, "required": True},
        "password": {"type": str, "min_length": 8, "max_length": 128, "required": True},
        "full_name": {"type": str, "max_length": 100, "required": False},
    },
    "article_creation": {
        "title": {"type": str, "max_length": 200, "required": True},
        "content": {
            "type": str,
            "format": "html",
            "max_length": 50000,
            "required": True,
        },
        "description": {"type": str, "max_length": 500, "required": False},
        "tags": {"type": list, "max_length": 10, "required": False},
    },
    "comment_creation": {
        "content": {"type": str, "max_length": 1000, "required": True},
        "parent_id": {"type": str, "required": False},
    },
}
