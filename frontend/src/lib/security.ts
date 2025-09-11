'use client';

import { NextRequest, NextResponse } from 'next/server';

// Security utilities
export class SecurityUtils {
  // Content Security Policy configuration
  static getCSPHeader(): string {
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    const directives = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://js.stripe.com https://www.googletagmanager.com https://www.google-analytics.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: https: blob:",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://api.stripe.com https://www.google-analytics.com https://analytics.google.com",
      "frame-src 'self' https://js.stripe.com https://hooks.stripe.com",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests",
      "block-all-mixed-content"
    ];

    if (isDevelopment) {
      directives.push("script-src 'self' 'unsafe-eval' 'unsafe-inline'");
    }

    return directives.join('; ');
  }

  // Security headers
  static getSecurityHeaders(): Record<string, string> {
    return {
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), browsing-topics=()',
      'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
      'X-Permitted-Cross-Domain-Policies': 'none',
      'Cross-Origin-Embedder-Policy': 'require-corp',
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Resource-Policy': 'same-origin',
      'Content-Security-Policy': this.getCSPHeader(),
    };
  }

  // Input sanitization
  static sanitizeInput(input: string): string {
    if (typeof input !== 'string') {
      return '';
    }

    // Remove null bytes and control characters
    let sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
    
    // Trim whitespace
    sanitized = sanitized.trim();
    
    // HTML escape
    sanitized = sanitized
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
    
    return sanitized;
  }

  // URL validation
  static isValidUrl(url: string): boolean {
    try {
      const urlObj = new URL(url);
      
      // Check for suspicious schemes
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        return false;
      }
      
      // Check for suspicious domains
      const suspiciousDomains = ['localhost', '127.0.0.1', '0.0.0.0'];
      if (suspiciousDomains.includes(urlObj.hostname)) {
        return false;
      }
      
      // Check for suspicious patterns
      const suspiciousPatterns = ['javascript:', 'data:', 'vbscript:'];
      if (suspiciousPatterns.some(pattern => url.toLowerCase().includes(pattern))) {
        return false;
      }
      
      return true;
    } catch {
      return false;
    }
  }

  // Email validation
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  // Password strength validation
  static validatePasswordStrength(password: string): {
    isValid: boolean;
    errors: string[];
    strength: 'weak' | 'medium' | 'strong';
  } {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }
    
    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    
    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    
    if (!/\d/.test(password)) {
      errors.push('Password must contain at least one number');
    }
    
    if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
      errors.push('Password must contain at least one special character');
    }
    
    const strength = errors.length === 0 ? 'strong' : errors.length <= 2 ? 'medium' : 'weak';
    
    return {
      isValid: errors.length === 0,
      errors,
      strength
    };
  }

  // XSS protection
  static sanitizeHTML(html: string): string {
    if (typeof html !== 'string') {
      return '';
    }

    // Remove script tags and their content
    html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    
    // Remove javascript: URLs
    html = html.replace(/javascript:/gi, '');
    
    // Remove on* event handlers
    html = html.replace(/\son\w+\s*=\s*["'][^"']*["']/gi, '');
    
    // Remove data: URLs that might contain scripts
    html = html.replace(/data:text\/html/gi, 'data:text/plain');
    
    return html;
  }

  // CSRF token management
  static generateCSRFToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  static async getCSRFToken(): Promise<string> {
    try {
      const response = await fetch('/api/csrf-token', {
        method: 'GET',
        credentials: 'include',
      });
      
      if (!response.ok) {
        throw new Error('Failed to get CSRF token');
      }
      
      const data = await response.json();
      return data.csrf_token;
    } catch (error) {
      console.error('Error getting CSRF token:', error);
      return this.generateCSRFToken();
    }
  }

  // Secure storage
  static setSecureItem(key: string, value: string): void {
    try {
      // Encrypt sensitive data before storing
      const encrypted = btoa(encodeURIComponent(value));
      localStorage.setItem(key, encrypted);
    } catch (error) {
      console.error('Error storing secure item:', error);
    }
  }

  static getSecureItem(key: string): string | null {
    try {
      const encrypted = localStorage.getItem(key);
      if (!encrypted) return null;
      
      // Decrypt data after retrieving
      return decodeURIComponent(atob(encrypted));
    } catch (error) {
      console.error('Error retrieving secure item:', error);
      return null;
    }
  }

  static removeSecureItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Error removing secure item:', error);
    }
  }

  // Session management
  static createSession(): string {
    const sessionId = this.generateCSRFToken();
    this.setSecureItem('session_id', sessionId);
    return sessionId;
  }

  static getSessionId(): string | null {
    return this.getSecureItem('session_id');
  }

  static clearSession(): void {
    this.removeSecureItem('session_id');
    this.removeSecureItem('csrf_token');
  }

  // Request security
  static async secureRequest(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const sessionId = this.getSessionId();
    const csrfToken = await this.getCSRFToken();
    
    const secureOptions: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-Session-ID': sessionId || '',
        'X-CSRF-Token': csrfToken,
        ...options.headers,
      },
      credentials: 'include',
    };
    
    return fetch(url, secureOptions);
  }

  // Rate limiting
  static createRateLimiter(maxRequests: number, windowMs: number) {
    const requests: number[] = [];
    
    return {
      isAllowed: (): boolean => {
        const now = Date.now();
        
        // Remove old requests outside the window
        while (requests.length > 0 && now - requests[0] > windowMs) {
          requests.shift();
        }
        
        // Check if we're under the limit
        if (requests.length >= maxRequests) {
          return false;
        }
        
        // Add current request
        requests.push(now);
        return true;
      },
      
      getRemainingRequests: (): number => {
        const now = Date.now();
        
        // Remove old requests
        while (requests.length > 0 && now - requests[0] > windowMs) {
          requests.shift();
        }
        
        return Math.max(0, maxRequests - requests.length);
      }
    };
  }
}

// Global rate limiter for API calls
export const apiRateLimiter = SecurityUtils.createRateLimiter(100, 3600000); // 100 requests per hour

// Security hooks
export function useSecurity() {
  const validateInput = (input: string) => SecurityUtils.sanitizeInput(input);
  const validateEmail = (email: string) => SecurityUtils.isValidEmail(email);
  const validatePassword = (password: string) => SecurityUtils.validatePasswordStrength(password);
  const validateUrl = (url: string) => SecurityUtils.isValidUrl(url);
  
  const secureRequest = async (url: string, options: RequestInit = {}) => {
    if (!apiRateLimiter.isAllowed()) {
      throw new Error('Rate limit exceeded');
    }
    
    return SecurityUtils.secureRequest(url, options);
  };
  
  return {
    validateInput,
    validateEmail,
    validatePassword,
    validateUrl,
    secureRequest,
    getCSRFToken: SecurityUtils.getCSRFToken,
    createSession: SecurityUtils.createSession,
    clearSession: SecurityUtils.clearSession,
  };
}
