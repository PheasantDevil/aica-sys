import { SEOUtils } from '@/lib/seo';

export async function GET() {
  const disallowPaths = [
    '/api/',
    '/admin/',
    '/dashboard/',
    '/settings/',
    '/checkout/',
    '/auth/',
    '/_next/',
    '/private/',
  ];

  const robotsTxt = SEOUtils.generateRobotsTxt(disallowPaths);

  return new Response(robotsTxt, {
    headers: {
      'Content-Type': 'text/plain',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400',
    },
  });
}
