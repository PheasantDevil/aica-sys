import { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: [
        '/dashboard/',
        '/admin/',
        '/api/',
        '/auth/',
        '/_next/',
        '/private/',
      ],
    },
    sitemap: 'https://aica-sys.com/sitemap.xml',
  };
}
