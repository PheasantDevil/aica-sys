import { NextRequest, NextResponse } from 'next/server';

const SITE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://aica-sys.vercel.app';

interface SitemapEntry {
  url: string;
  lastModified: Date;
  changeFrequency: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  priority: number;
}

export async function GET(request: NextRequest) {
  try {
    // 静的ページのサイトマップエントリ
    const staticPages: SitemapEntry[] = [
      {
        url: `${SITE_URL}/`,
        lastModified: new Date(),
        changeFrequency: 'daily',
        priority: 1.0,
      },
      {
        url: `${SITE_URL}/articles`,
        lastModified: new Date(),
        changeFrequency: 'daily',
        priority: 0.9,
      },
      {
        url: `${SITE_URL}/newsletters`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
      },
      {
        url: `${SITE_URL}/trends`,
        lastModified: new Date(),
        changeFrequency: 'daily',
        priority: 0.8,
      },
      {
        url: `${SITE_URL}/pricing`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.7,
      },
      {
        url: `${SITE_URL}/about`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.6,
      },
      {
        url: `${SITE_URL}/contact`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.6,
      },
      {
        url: `${SITE_URL}/privacy-policy`,
        lastModified: new Date(),
        changeFrequency: 'yearly',
        priority: 0.3,
      },
      {
        url: `${SITE_URL}/terms-of-service`,
        lastModified: new Date(),
        changeFrequency: 'yearly',
        priority: 0.3,
      },
    ];

    // 動的コンテンツのサイトマップエントリを取得
    const dynamicPages = await getDynamicPages();

    // サイトマップエントリを結合
    const allPages = [...staticPages, ...dynamicPages];

    // XMLサイトマップを生成
    const sitemap = generateSitemapXML(allPages);

    return new NextResponse(sitemap, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    });
  } catch (error) {
    console.error('Error generating sitemap:', error);
    return new NextResponse('Error generating sitemap', { status: 500 });
  }
}

async function getDynamicPages(): Promise<SitemapEntry[]> {
  const dynamicPages: SitemapEntry[] = [];

  try {
    // 記事のサイトマップエントリを取得
    const articles = await getArticles();
    articles.forEach(article => {
      dynamicPages.push({
        url: `${SITE_URL}/articles/${article.slug}`,
        lastModified: new Date(article.updatedAt || article.createdAt),
        changeFrequency: 'weekly',
        priority: 0.8,
      });
    });

    // ニュースレターのサイトマップエントリを取得
    const newsletters = await getNewsletters();
    newsletters.forEach(newsletter => {
      dynamicPages.push({
        url: `${SITE_URL}/newsletters/${newsletter.slug}`,
        lastModified: new Date(newsletter.updatedAt || newsletter.createdAt),
        changeFrequency: 'monthly',
        priority: 0.7,
      });
    });

    // トレンドのサイトマップエントリを取得
    const trends = await getTrends();
    trends.forEach(trend => {
      dynamicPages.push({
        url: `${SITE_URL}/trends/${trend.slug}`,
        lastModified: new Date(trend.updatedAt || trend.createdAt),
        changeFrequency: 'daily',
        priority: 0.7,
      });
    });

  } catch (error) {
    console.error('Error fetching dynamic pages:', error);
  }

  return dynamicPages;
}

async function getArticles(): Promise<Array<{slug: string, createdAt: string, updatedAt?: string}>> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/content/articles?limit=1000`, {
      next: { revalidate: 3600 }, // 1時間キャッシュ
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch articles: ${response.status}`);
    }

    const data = await response.json();
    return data.articles?.map((article: any) => ({
      slug: article.title?.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') || `article-${article.id}`,
      createdAt: article.created_at,
      updatedAt: article.updated_at,
    })) || [];
  } catch (error) {
    console.error('Error fetching articles for sitemap:', error);
    return [];
  }
}

async function getNewsletters(): Promise<Array<{slug: string, createdAt: string, updatedAt?: string}>> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/content/newsletters?limit=1000`, {
      next: { revalidate: 3600 }, // 1時間キャッシュ
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch newsletters: ${response.status}`);
    }

    const data = await response.json();
    return data.newsletters?.map((newsletter: any) => ({
      slug: newsletter.title?.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') || `newsletter-${newsletter.id}`,
      createdAt: newsletter.created_at,
      updatedAt: newsletter.updated_at,
    })) || [];
  } catch (error) {
    console.error('Error fetching newsletters for sitemap:', error);
    return [];
  }
}

async function getTrends(): Promise<Array<{slug: string, createdAt: string, updatedAt?: string}>> {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/api/content/trends?limit=1000`, {
      next: { revalidate: 3600 }, // 1時間キャッシュ
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch trends: ${response.status}`);
    }

    const data = await response.json();
    return data.trends?.map((trend: any) => ({
      slug: trend.title?.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '') || `trend-${trend.id}`,
      createdAt: trend.created_at,
      updatedAt: trend.updated_at,
    })) || [];
  } catch (error) {
    console.error('Error fetching trends for sitemap:', error);
    return [];
  }
}

function generateSitemapXML(pages: SitemapEntry[]): string {
  const xmlHeader = '<?xml version="1.0" encoding="UTF-8"?>';
  const urlsetOpen = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">';
  const urlsetClose = '</urlset>';

  const urlEntries = pages.map(page => {
    return `
  <url>
    <loc>${page.url}</loc>
    <lastmod>${page.lastModified.toISOString()}</lastmod>
    <changefreq>${page.changeFrequency}</changefreq>
    <priority>${page.priority}</priority>
  </url>`;
  }).join('');

  return `${xmlHeader}
${urlsetOpen}${urlEntries}
${urlsetClose}`;
}