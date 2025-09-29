import { Metadata } from 'next';

export interface SEOData {
  title: string;
  description: string;
  keywords?: string[];
  canonical?: string;
  ogImage?: string;
  ogType?: 'website' | 'article';
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player';
  noindex?: boolean;
  nofollow?: boolean;
  structuredData?: Record<string, any>;
}

export class SEOUtils {
  private static baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://aica-sys.vercel.app';
  private static siteName = 'AICA-SyS';
  private static defaultDescription = 'AI駆動型TypeScriptエコシステム特化型の自動コンテンツ生成・販売システム';
  private static defaultKeywords = [
    'TypeScript',
    'AI',
    '自動コンテンツ生成',
    'プログラミング',
    '開発ツール',
    '技術情報',
    'キュレーション',
    'サブスクリプション'
  ];

  static generateMetadata(data: SEOData): Metadata {
    const {
      title,
      description,
      keywords = [],
      canonical,
      ogImage,
      ogType = 'website',
      twitterCard = 'summary_large_image',
      noindex = false,
      nofollow = false,
      structuredData
    } = data;

    const fullTitle = title.includes(this.siteName) ? title : `${title} | ${this.siteName}`;
    const fullDescription = description || this.defaultDescription;
    const fullKeywords = [...this.defaultKeywords, ...keywords];
    const canonicalUrl = canonical || this.baseUrl;
    const ogImageUrl = ogImage || `${this.baseUrl}/og-image.jpg`;

    return {
      title: fullTitle,
      description: fullDescription,
      keywords: fullKeywords.join(', '),
      authors: [{ name: this.siteName }],
      creator: this.siteName,
      publisher: this.siteName,
      robots: {
        index: !noindex,
        follow: !nofollow,
        googleBot: {
          index: !noindex,
          follow: !nofollow,
          'max-video-preview': -1,
          'max-image-preview': 'large',
          'max-snippet': -1,
        },
      },
      openGraph: {
        type: ogType,
        locale: 'ja_JP',
        url: canonicalUrl,
        title: fullTitle,
        description: fullDescription,
        siteName: this.siteName,
        images: [
          {
            url: ogImageUrl,
            width: 1200,
            height: 630,
            alt: fullTitle,
          },
        ],
      },
      twitter: {
        card: twitterCard,
        title: fullTitle,
        description: fullDescription,
        images: [ogImageUrl],
        creator: '@aica_sys',
        site: '@aica_sys',
      },
      alternates: {
        canonical: canonicalUrl,
      },
      other: {
        'application-name': this.siteName,
        'apple-mobile-web-app-title': this.siteName,
        'msapplication-TileColor': '#000000',
        'theme-color': '#000000',
      },
    };
  }

  static generateStructuredData(type: 'website' | 'article' | 'organization' | 'breadcrumb', data: any) {
    const baseStructuredData = {
      '@context': 'https://schema.org',
      '@type': type === 'website' ? 'WebSite' : 
               type === 'article' ? 'Article' :
               type === 'organization' ? 'Organization' : 'BreadcrumbList',
    };

    switch (type) {
      case 'website':
        return {
          ...baseStructuredData,
          name: this.siteName,
          description: this.defaultDescription,
          url: this.baseUrl,
          potentialAction: {
            '@type': 'SearchAction',
            target: `${this.baseUrl}/search?q={search_term_string}`,
            'query-input': 'required name=search_term_string',
          },
        };

      case 'article':
        return {
          ...baseStructuredData,
          headline: data.title,
          description: data.description,
          image: data.image || `${this.baseUrl}/og-image.jpg`,
          author: {
            '@type': 'Person',
            name: data.author || this.siteName,
          },
          publisher: {
            '@type': 'Organization',
            name: this.siteName,
            logo: {
              '@type': 'ImageObject',
              url: `${this.baseUrl}/logo.png`,
            },
          },
          datePublished: data.publishedAt,
          dateModified: data.updatedAt || data.publishedAt,
          mainEntityOfPage: {
            '@type': 'WebPage',
            '@id': data.url || this.baseUrl,
          },
        };

      case 'organization':
        return {
          ...baseStructuredData,
          name: this.siteName,
          description: this.defaultDescription,
          url: this.baseUrl,
          logo: `${this.baseUrl}/logo.png`,
          sameAs: [
            'https://twitter.com/aica_sys',
            'https://github.com/PheasantDevil/aica-sys',
          ],
        };

      case 'breadcrumb':
        return {
          ...baseStructuredData,
          itemListElement: data.items.map((item: any, index: number) => ({
            '@type': 'ListItem',
            position: index + 1,
            name: item.name,
            item: item.url,
          })),
        };

      default:
        return baseStructuredData;
    }
  }

  static generateSitemapData(pages: Array<{
    url: string;
    lastModified: string;
    changeFrequency: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
    priority: number;
  }>) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  ${pages.map(page => `
    <url>
      <loc>${this.baseUrl}${page.url}</loc>
      <lastmod>${page.lastModified}</lastmod>
      <changefreq>${page.changeFrequency}</changefreq>
      <priority>${page.priority}</priority>
    </url>
  `).join('')}
</urlset>`;
  }

  static generateRobotsTxt(disallowPaths: string[] = []) {
    const disallowRules = disallowPaths.map(path => `Disallow: ${path}`).join('\n');
    
    return `User-agent: *
Allow: /

${disallowRules}

Sitemap: ${this.baseUrl}/sitemap.xml
Host: ${this.baseUrl}`;
  }

  static optimizeTitle(title: string, maxLength: number = 60): string {
    if (title.length <= maxLength) return title;
    
    const words = title.split(' ');
    let optimized = '';
    
    for (const word of words) {
      if ((optimized + ' ' + word).length <= maxLength) {
        optimized += (optimized ? ' ' : '') + word;
      } else {
        break;
      }
    }
    
    return optimized || title.substring(0, maxLength - 3) + '...';
  }

  static optimizeDescription(description: string, maxLength: number = 160): string {
    if (description.length <= maxLength) return description;
    
    return description.substring(0, maxLength - 3) + '...';
  }

  static extractKeywords(text: string, maxKeywords: number = 10): string[] {
    // Simple keyword extraction (in production, use more sophisticated NLP)
    const words = text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 3);
    
    const wordCount: Record<string, number> = {};
    words.forEach(word => {
      wordCount[word] = (wordCount[word] || 0) + 1;
    });
    
    return Object.entries(wordCount)
      .sort(([, a], [, b]) => b - a)
      .slice(0, maxKeywords)
      .map(([word]) => word);
  }

  static generateCanonicalUrl(path: string): string {
    return `${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`;
  }

  static generateOGImageUrl(title: string, description?: string): string {
    const params = new URLSearchParams({
      title: this.optimizeTitle(title, 50),
      description: description ? this.optimizeDescription(description, 100) : '',
      theme: 'dark',
    });
    
    return `${this.baseUrl}/api/og?${params.toString()}`;
  }
}

// SEO hooks
export function useSEO() {
  const generateMetadata = (data: SEOData) => SEOUtils.generateMetadata(data);
  const generateStructuredData = (type: 'website' | 'article' | 'organization' | 'breadcrumb', data: any) => 
    SEOUtils.generateStructuredData(type, data);
  const optimizeTitle = (title: string, maxLength?: number) => SEOUtils.optimizeTitle(title, maxLength);
  const optimizeDescription = (description: string, maxLength?: number) => SEOUtils.optimizeDescription(description, maxLength);
  const extractKeywords = (text: string, maxKeywords?: number) => SEOUtils.extractKeywords(text, maxKeywords);
  const generateCanonicalUrl = (path: string) => SEOUtils.generateCanonicalUrl(path);
  const generateOGImageUrl = (title: string, description?: string) => SEOUtils.generateOGImageUrl(title, description);

  return {
    generateMetadata,
    generateStructuredData,
    optimizeTitle,
    optimizeDescription,
    extractKeywords,
    generateCanonicalUrl,
    generateOGImageUrl,
  };
}