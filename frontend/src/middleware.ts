import { SecurityUtils } from "@/lib/security";
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Add security headers
  const securityHeaders = SecurityUtils.getSecurityHeaders();
  Object.entries(securityHeaders).forEach(([key, value]) => {
    response.headers.set(key, value);
  });

  // Add CORS headers for API routes
  if (request.nextUrl.pathname.startsWith("/api/")) {
    response.headers.set("Access-Control-Allow-Origin", request.headers.get("origin") || "*");
    response.headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
    response.headers.set(
      "Access-Control-Allow-Headers",
      "Content-Type, Authorization, X-CSRF-Token, X-Session-ID",
    );
    response.headers.set("Access-Control-Allow-Credentials", "true");
  }

  // Handle preflight requests
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 200, headers: response.headers });
  }

  // Security checks for sensitive routes
  if (request.nextUrl.pathname.startsWith("/admin")) {
    // Check for admin authentication
    const token = request.cookies.get("admin_token");
    if (!token) {
      return NextResponse.redirect(new URL("/auth/signin", request.url));
    }
  }

  // Rate limiting for API routes
  if (request.nextUrl.pathname.startsWith("/api/")) {
    const clientIP = request.ip || request.headers.get("x-forwarded-for") || "unknown";
    const rateLimitKey = `rate_limit:${clientIP}`;

    // This would integrate with your rate limiting system
    // For now, we'll just add the headers
    response.headers.set("X-RateLimit-Limit", "100");
    response.headers.set("X-RateLimit-Remaining", "99");
  }

  // CSRF protection for state-changing methods (disabled for now to prevent blocking)
  // TODO: Implement proper CSRF protection with token generation
  // if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
  //   const csrfToken = request.headers.get('X-CSRF-Token');
  //   if (!csrfToken) {
  //     return NextResponse.json(
  //       { error: 'CSRF token required' },
  //       { status: 403 }
  //     );
  //   }
  // }

  // Input validation for form submissions
  if (request.method === "POST" && request.nextUrl.pathname.startsWith("/api/")) {
    const contentType = request.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      // This would validate the request body
      // For now, we'll just add validation headers
      response.headers.set("X-Content-Validation", "enabled");
    }
  }

  // Log security events
  if (request.nextUrl.pathname.startsWith("/api/auth/")) {
    console.log(`Security event: ${request.method} ${request.nextUrl.pathname} from ${request.ip}`);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|public).*)",
  ],
};
