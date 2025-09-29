import { Metadata } from 'next';

export interface SEOConfig {
  title: string;
  description: string;
  keywords?: string[];
  canonical?: string;
  ogImage?: string;
  ogType?: 'website' | 'article' | 'profile';
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player';
  noindex?: boolean;
  nofollow?: boolean;
  structuredData?: Record<string, any>;
}

export interface ArticleSEOData {
  title: string;
  description: string;
  content: string;
  author: string;
  publishedAt: string;
  modifiedAt?: string;
  image?: string;
  tags?: string[];
  category?: string;
  readingTime?: number;
}

export interface OrganizationSEOData {
  name: string;
  description: string;
  url: string;
  logo?: string;
  socialProfiles?: {
    twitter?: string;
    facebook?: string;
    linkedin?: string;
    github?: string;
  };
}

export class AdvancedSEO {
  private static readonly DEFAULT_CONFIG = {
    siteName: 'AICA-SyS',
    siteUrl: process.env.NEXT_PUBLIC_BASE_URL || 'https://aica-sys.vercel.app',
    defaultImage: '/og-default.png',
    twitterHandle: '@aica_sys',
  };

  /**
   * ページ用のメタデータを生成
   */
  static generateMetadata(config: SEOConfig): Metadata {
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
    } = config;

    const fullTitle = title.includes(this.DEFAULT_CONFIG.siteName) 
      ? title 
      : `${title} | ${this.DEFAULT_CONFIG.siteName}`;

    const imageUrl = ogImage 
      ? `${this.DEFAULT_CONFIG.siteUrl}${ogImage}`
      : `${this.DEFAULT_CONFIG.siteUrl}${this.DEFAULT_CONFIG.defaultImage}`;

    const canonicalUrl = canonical 
      ? `${this.DEFAULT_CONFIG.siteUrl}${canonical}`
      : undefined;

    return {
      title: fullTitle,
      description,
      keywords: keywords.join(', '),
      canonical: canonicalUrl,
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
        title: fullTitle,
        description,
        url: canonicalUrl,
        siteName: this.DEFAULT_CONFIG.siteName,
        images: [
          {
            url: imageUrl,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
      twitter: {
        card: twitterCard,
        title: fullTitle,
        description,
        images: [imageUrl],
        creator: this.DEFAULT_CONFIG.twitterHandle,
      },
      alternates: {
        canonical: canonicalUrl,
      },
    };
  }

  /**
   * 記事用のメタデータを生成
   */
  static generateArticleMetadata(article: ArticleSEOData): Metadata {
    const config: SEOConfig = {
      title: article.title,
      description: article.description,
      keywords: article.tags,
      canonical: `/articles/${article.title.toLowerCase().replace(/\s+/g, '-')}`,
      ogImage: article.image,
      ogType: 'article',
      twitterCard: 'summary_large_image',
      structuredData: this.generateArticleStructuredData(article),
    };

    return this.generateMetadata(config);
  }

  /**
   * 記事の構造化データを生成
   */
  static generateArticleStructuredData(article: ArticleSEOData): Record<string, any> {
    return {
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: article.title,
      description: article.description,
      image: article.image ? `${this.DEFAULT_CONFIG.siteUrl}${article.image}` : undefined,
      author: {
        '@type': 'Person',
        name: article.author,
      },
      publisher: {
        '@type': 'Organization',
        name: this.DEFAULT_CONFIG.siteName,
        logo: {
          '@type': 'ImageObject',
          url: `${this.DEFAULT_CONFIG.siteUrl}/logo.png`,
        },
      },
      datePublished: article.publishedAt,
      dateModified: article.modifiedAt || article.publishedAt,
      mainEntityOfPage: {
        '@type': 'WebPage',
        '@id': `${this.DEFAULT_CONFIG.siteUrl}/articles/${article.title.toLowerCase().replace(/\s+/g, '-')}`,
      },
      keywords: article.tags?.join(', '),
      articleSection: article.category,
      wordCount: article.content.split(' ').length,
      timeRequired: article.readingTime ? `PT${article.readingTime}M` : undefined,
    };
  }

  /**
   * 組織の構造化データを生成
   */
  static generateOrganizationStructuredData(org: OrganizationSEOData): Record<string, any> {
    const socialProfiles = org.socialProfiles ? Object.entries(org.socialProfiles)
      .filter(([_, url]) => url)
      .map(([platform, url]) => ({
        '@type': 'ProfilePage',
        name: platform,
        url: url,
      })) : [];

    return {
      '@context': 'https://schema.org',
      '@type': 'Organization',
      name: org.name,
      description: org.description,
      url: org.url,
      logo: org.logo ? `${this.DEFAULT_CONFIG.siteUrl}${org.logo}` : undefined,
      sameAs: socialProfiles.map(profile => profile.url),
      contactPoint: {
        '@type': 'ContactPoint',
        contactType: 'customer service',
        url: `${org.url}/contact`,
      },
    };
  }

  /**
   * Webサイトの構造化データを生成
   */
  static generateWebsiteStructuredData(): Record<string, any> {
    return {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: this.DEFAULT_CONFIG.siteName,
      url: this.DEFAULT_CONFIG.siteUrl,
      description: 'AI-driven Content Curation & Automated Sales System for TypeScript ecosystem',
      potentialAction: {
        '@type': 'SearchAction',
        target: {
          '@type': 'EntryPoint',
          urlTemplate: `${this.DEFAULT_CONFIG.siteUrl}/search?q={search_term_string}`,
        },
        'query-input': 'required name=search_term_string',
      },
    };
  }

  /**
   * パンくずリストの構造化データを生成
   */
  static generateBreadcrumbStructuredData(breadcrumbs: Array<{name: string, url: string}>): Record<string, any> {
    return {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: breadcrumbs.map((crumb, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        name: crumb.name,
        item: `${this.DEFAULT_CONFIG.siteUrl}${crumb.url}`,
      })),
    };
  }

  /**
   * FAQの構造化データを生成
   */
  static generateFAQStructuredData(faqs: Array<{question: string, answer: string}>): Record<string, any> {
    return {
      '@context': 'https://schema.org',
      '@type': 'FAQPage',
      mainEntity: faqs.map(faq => ({
        '@type': 'Question',
        name: faq.question,
        acceptedAnswer: {
          '@type': 'Answer',
          text: faq.answer,
        },
      })),
    };
  }

  /**
   * 商品の構造化データを生成
   */
  static generateProductStructuredData(product: {
    name: string;
    description: string;
    price: number;
    currency: string;
    availability: 'InStock' | 'OutOfStock' | 'PreOrder';
    image?: string;
    brand?: string;
    category?: string;
  }): Record<string, any> {
    return {
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: product.name,
      description: product.description,
      image: product.image ? `${this.DEFAULT_CONFIG.siteUrl}${product.image}` : undefined,
      brand: product.brand ? {
        '@type': 'Brand',
        name: product.brand,
      } : undefined,
      category: product.category,
      offers: {
        '@type': 'Offer',
        price: product.price,
        priceCurrency: product.currency,
        availability: `https://schema.org/${product.availability}`,
        seller: {
          '@type': 'Organization',
          name: this.DEFAULT_CONFIG.siteName,
        },
      },
    };
  }

  /**
   * キーワード密度を計算
   */
  static calculateKeywordDensity(content: string, keyword: string): number {
    const words = content.toLowerCase().split(/\s+/);
    const keywordCount = words.filter(word => word.includes(keyword.toLowerCase())).length;
    return (keywordCount / words.length) * 100;
  }

  /**
   * 読みやすさスコアを計算（簡易版）
   */
  static calculateReadabilityScore(content: string): number {
    const sentences = content.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const words = content.split(/\s+/).filter(w => w.length > 0);
    const syllables = words.reduce((total, word) => total + this.countSyllables(word), 0);

    const avgWordsPerSentence = words.length / sentences.length;
    const avgSyllablesPerWord = syllables / words.length;

    // 簡易Flesch Reading Ease式
    const score = 206.835 - (1.015 * avgWordsPerSentence) - (84.6 * avgSyllablesPerWord);
    return Math.max(0, Math.min(100, score));
  }

  /**
   * 音節数を計算（簡易版）
   */
  private static countSyllables(word: string): number {
    const vowels = 'aeiouy';
    let count = 0;
    let previousWasVowel = false;

    for (let i = 0; i < word.length; i++) {
      const isVowel = vowels.includes(word[i].toLowerCase());
      if (isVowel && !previousWasVowel) {
        count++;
      }
      previousWasVowel = isVowel;
    }

    // 最後が'e'で終わる場合は音節を減らす
    if (word.endsWith('e') && count > 1) {
      count--;
    }

    return Math.max(1, count);
  }

  /**
   * メタタグの最適化提案を生成
   */
  static generateOptimizationSuggestions(config: SEOConfig): string[] {
    const suggestions: string[] = [];

    // タイトル長チェック
    if (config.title.length < 30) {
      suggestions.push('タイトルが短すぎます。30-60文字を推奨します。');
    } else if (config.title.length > 60) {
      suggestions.push('タイトルが長すぎます。60文字以下を推奨します。');
    }

    // 説明文長チェック
    if (config.description.length < 120) {
      suggestions.push('メタディスクリプションが短すぎます。120-160文字を推奨します。');
    } else if (config.description.length > 160) {
      suggestions.push('メタディスクリプションが長すぎます。160文字以下を推奨します。');
    }

    // キーワードチェック
    if (!config.keywords || config.keywords.length === 0) {
      suggestions.push('キーワードが設定されていません。');
    } else if (config.keywords.length > 10) {
      suggestions.push('キーワードが多すぎます。5-10個を推奨します。');
    }

    return suggestions;
  }
}

/**
 * SEOコンポーネント用のフック
 */
export function useSEO() {
  const generatePageSEO = (config: SEOConfig) => {
    return AdvancedSEO.generateMetadata(config);
  };

  const generateArticleSEO = (article: ArticleSEOData) => {
    return AdvancedSEO.generateArticleMetadata(article);
  };

  const generateStructuredData = (type: string, data: any) => {
    switch (type) {
      case 'article':
        return AdvancedSEO.generateArticleStructuredData(data);
      case 'organization':
        return AdvancedSEO.generateOrganizationStructuredData(data);
      case 'website':
        return AdvancedSEO.generateWebsiteStructuredData();
      case 'breadcrumb':
        return AdvancedSEO.generateBreadcrumbStructuredData(data);
      case 'faq':
        return AdvancedSEO.generateFAQStructuredData(data);
      case 'product':
        return AdvancedSEO.generateProductStructuredData(data);
      default:
        return null;
    }
  };

  const analyzeContent = (content: string, keyword: string) => {
    return {
      keywordDensity: AdvancedSEO.calculateKeywordDensity(content, keyword),
      readabilityScore: AdvancedSEO.calculateReadabilityScore(content),
    };
  };

  return {
    generatePageSEO,
    generateArticleSEO,
    generateStructuredData,
    analyzeContent,
  };
}
