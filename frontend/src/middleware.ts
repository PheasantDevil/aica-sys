import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { rateLimit, rateLimiters } from '@/lib/rate-limit';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // セキュリティヘッダーの追加
  const response = NextResponse.next();

  // セキュリティヘッダーを追加
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), browsing-topics=()');

  // HTTPS強制（本番環境のみ）
  if (process.env.NODE_ENV === 'production') {
    response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
  }

  // レート制限の適用
  if (pathname.startsWith('/api/')) {
    // API エンドポイントのレート制限
    if (pathname.startsWith('/api/auth/')) {
      // 認証関連のレート制限
      return applyRateLimit(request, rateLimiters.auth);
    } else if (pathname.startsWith('/api/search')) {
      // 検索のレート制限
      return applyRateLimit(request, rateLimiters.search);
    } else if (pathname.startsWith('/api/upload')) {
      // アップロードのレート制限
      return applyRateLimit(request, rateLimiters.upload);
    } else {
      // 一般的なAPIのレート制限
      return applyRateLimit(request, rateLimiters.api);
    }
  }

  // 管理者ページのアクセス制御
  if (pathname.startsWith('/admin')) {
    // 管理者権限のチェック（実際の実装では適切な認証チェックを実装）
    const isAdmin = request.cookies.get('admin')?.value === 'true';
    if (!isAdmin) {
      return NextResponse.redirect(new URL('/unauthorized', request.url));
    }
  }

  // 危険なパスのブロック
  const dangerousPaths = [
    '/.env',
    '/.git',
    '/wp-admin',
    '/wp-login',
    '/admin.php',
    '/phpmyadmin',
    '/.htaccess',
    '/.htpasswd',
  ];

  if (dangerousPaths.some(path => pathname.startsWith(path))) {
    return new NextResponse('Not Found', { status: 404 });
  }

  // ファイル拡張子のブロック
  const blockedExtensions = ['.php', '.asp', '.jsp', '.cgi', '.pl'];
  if (blockedExtensions.some(ext => pathname.endsWith(ext))) {
    return new NextResponse('Not Found', { status: 404 });
  }

  return response;
}

async function applyRateLimit(request: NextRequest, limiter: any) {
  const rateLimitResponse = await rateLimit(request, limiter);
  
  if (rateLimitResponse) {
    return rateLimitResponse;
  }

  return NextResponse.next();
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
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
};
