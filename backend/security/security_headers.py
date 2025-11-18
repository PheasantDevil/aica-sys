"""
Security Headers Middleware
Implements comprehensive security headers for API responses
"""

import logging
from typing import Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to all responses"""

    def __init__(self, app, config: Optional[Dict[str, any]] = None):
        super().__init__(app)
        self.config = config or self._get_default_config()

    def _get_default_config(self) -> Dict[str, any]:
        """Get default security headers configuration"""
        return {
            "x_frame_options": "DENY",
            "x_content_type_options": "nosniff",
            "x_xss_protection": "1; mode=block",
            "referrer_policy": "strict-origin-when-cross-origin",
            "permissions_policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
            "strict_transport_security": "max-age=31536000; includeSubDomains; preload",
            "content_security_policy": self._get_default_csp(),
            "cross_origin_embedder_policy": "require-corp",
            "cross_origin_opener_policy": "same-origin",
            "cross_origin_resource_policy": "same-origin",
            "x_dns_prefetch_control": "off",
            "x_download_options": "noopen",
            "x_permitted_cross_domain_policies": "none",
            "expect_ct": "max-age=86400, enforce",
            "feature_policy": "camera 'none'; microphone 'none'; geolocation 'none'; payment 'none'; usb 'none'",
        }

    def _get_default_csp(self) -> str:
        """Get default Content Security Policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://vercel.live; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https://*.supabase.co https://*.vercel.app wss://*.vercel.app; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content"
        )

    async def dispatch(self, request: Request, call_next):
        """Process request and add security headers"""
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        # Add custom headers based on request
        self._add_custom_headers(request, response)

        return response

    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        headers_to_add = {
            "X-Frame-Options": self.config["x_frame_options"],
            "X-Content-Type-Options": self.config["x_content_type_options"],
            "X-XSS-Protection": self.config["x_xss_protection"],
            "Referrer-Policy": self.config["referrer_policy"],
            "Permissions-Policy": self.config["permissions_policy"],
            "Strict-Transport-Security": self.config["strict_transport_security"],
            "Content-Security-Policy": self.config["content_security_policy"],
            "Cross-Origin-Embedder-Policy": self.config["cross_origin_embedder_policy"],
            "Cross-Origin-Opener-Policy": self.config["cross_origin_opener_policy"],
            "Cross-Origin-Resource-Policy": self.config["cross_origin_resource_policy"],
            "X-DNS-Prefetch-Control": self.config["x_dns_prefetch_control"],
            "X-Download-Options": self.config["x_download_options"],
            "X-Permitted-Cross-Domain-Policies": self.config[
                "x_permitted_cross_domain_policies"
            ],
            "Expect-CT": self.config["expect_ct"],
            "Feature-Policy": self.config["feature_policy"],
        }

        for header, value in headers_to_add.items():
            if value and header not in response.headers:
                response.headers[header] = value

    def _add_custom_headers(self, request: Request, response: Response):
        """Add custom headers based on request context"""
        # Add cache control headers for sensitive endpoints
        if request.url.path.startswith("/api/auth/") or request.url.path.startswith(
            "/api/admin/"
        ):
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, private"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        # Add CORS headers for API endpoints
        if request.url.path.startswith("/api/"):
            response.headers["Access-Control-Allow-Origin"] = self._get_allowed_origin(
                request
            )
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, DELETE, OPTIONS"
            )
            response.headers["Access-Control-Allow-Headers"] = (
                "Content-Type, Authorization, X-Requested-With"
            )
            response.headers["Access-Control-Max-Age"] = "86400"

        # Add server information (optional)
        response.headers["Server"] = "AICA-SyS/1.0"

        # Add request ID for tracking
        if hasattr(request.state, "request_id"):
            response.headers["X-Request-ID"] = request.state.request_id

    def _get_allowed_origin(self, request: Request) -> str:
        """Get allowed origin for CORS"""
        origin = request.headers.get("origin")
        allowed_origins = [
            "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app",
            "https://aica-sys.vercel.app",
            "http://localhost:3000",
            "http://localhost:3001",
        ]

        if origin in allowed_origins:
            return origin
        return "https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app"


class SecurityConfig:
    """Security configuration class"""

    def __init__(self):
        self.csp_policy = self._get_default_csp()
        self.hsts_max_age = 31536000  # 1 year
        self.hsts_include_subdomains = True
        self.hsts_preload = True
        self.frame_options = "DENY"
        self.content_type_options = "nosniff"
        self.xss_protection = "1; mode=block"
        self.referrer_policy = "strict-origin-when-cross-origin"

    def _get_default_csp(self) -> str:
        """Get default CSP policy"""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://vercel.live; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https://*.supabase.co https://*.vercel.app wss://*.vercel.app; "
            "frame-src 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content"
        )

    def update_csp(self, directive: str, values: List[str]):
        """Update CSP directive"""
        # This is a simplified implementation
        # In production, use a proper CSP parser
        pass

    def get_csp_header(self) -> str:
        """Get CSP header value"""
        return self.csp_policy

    def get_hsts_header(self) -> str:
        """Get HSTS header value"""
        hsts = f"max-age={self.hsts_max_age}"
        if self.hsts_include_subdomains:
            hsts += "; includeSubDomains"
        if self.hsts_preload:
            hsts += "; preload"
        return hsts


# Security headers for different environments
DEVELOPMENT_HEADERS = {
    "x_frame_options": "SAMEORIGIN",
    "content_security_policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:;",
    "strict_transport_security": "max-age=86400; includeSubDomains",
}

PRODUCTION_HEADERS = {
    "x_frame_options": "DENY",
    "content_security_policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://vercel.live; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://*.supabase.co https://*.vercel.app; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; upgrade-insecure-requests; block-all-mixed-content",
    "strict_transport_security": "max-age=31536000; includeSubDomains; preload",
}


def get_security_headers(environment: str = "production") -> Dict[str, str]:
    """Get security headers for environment"""
    if environment == "development":
        return DEVELOPMENT_HEADERS
    return PRODUCTION_HEADERS


# Security header validation
def validate_security_headers(headers: Dict[str, str]) -> List[str]:
    """Validate security headers and return warnings"""
    warnings = []

    # Check for missing critical headers
    critical_headers = [
        "X-Frame-Options",
        "X-Content-Type-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
    ]

    for header in critical_headers:
        if header not in headers:
            warnings.append(f"Missing critical security header: {header}")

    # Check CSP policy
    csp = headers.get("Content-Security-Policy", "")
    if not csp:
        warnings.append("Missing Content-Security-Policy header")
    elif "unsafe-inline" in csp and "unsafe-eval" in csp:
        warnings.append("CSP policy contains unsafe directives")

    # Check HSTS configuration
    hsts = headers.get("Strict-Transport-Security", "")
    if hsts and "max-age=0" in hsts:
        warnings.append("HSTS max-age is set to 0, which disables HSTS")

    return warnings
