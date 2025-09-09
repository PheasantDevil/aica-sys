import { NextSeoProps } from 'next-seo';

// サイト全体のSEO設定
export const defaultSEO: NextSeoProps = {
  title: 'AICA-SyS - AI-driven Content Curation & Automated Sales System',
  titleTemplate: '%s | AICA-SyS',
  description: 'TypeScriptエコシステム特化型のAI自動コンテンツ生成・販売システム。高品質な技術記事、ニュースレター、トレンド分析を自動生成し、月額¥10,000以上の収益を実現。',
  canonical: 'https://aica-sys.com',
  openGraph: {
    type: 'website',
    locale: 'ja_JP',
    url: 'https://aica-sys.com',
    siteName: 'AICA-SyS',
    title: 'AICA-SyS - AI-driven Content Curation & Automated Sales System',
    description: 'TypeScriptエコシステム特化型のAI自動コンテンツ生成・販売システム',
    images: [
      {
        url: 'https://aica-sys.com/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'AICA-SyS - AI-driven Content Curation & Automated Sales System',
      },
    ],
  },
  twitter: {
    handle: '@aica_sys',
    site: '@aica_sys',
    cardType: 'summary_large_image',
  },
  additionalMetaTags: [
    {
      name: 'keywords',
      content: 'TypeScript, AI, コンテンツ生成, 自動販売, 技術記事, ニュースレター, トレンド分析, プログラミング, 開発者向け',
    },
    {
      name: 'author',
      content: 'AICA-SyS Team',
    },
    {
      name: 'robots',
      content: 'index, follow',
    },
    {
      name: 'googlebot',
      content: 'index, follow',
    },
    {
      name: 'viewport',
      content: 'width=device-width, initial-scale=1',
    },
  ],
  additionalLinkTags: [
    {
      rel: 'icon',
      href: '/favicon.ico',
    },
    {
      rel: 'apple-touch-icon',
      href: '/apple-touch-icon.png',
      sizes: '180x180',
    },
    {
      rel: 'manifest',
      href: '/manifest.json',
    },
  ],
};

// ページ別SEO設定
export const pageSEO = {
  home: {
    title: 'ホーム',
    description: 'AICA-SySはTypeScriptエコシステムに特化したAI自動コンテンツ生成・販売システムです。高品質な技術記事、ニュースレター、トレンド分析を自動生成し、月額¥10,000以上の収益を実現します。',
    keywords: 'TypeScript, AI, コンテンツ生成, 自動販売, 技術記事, ニュースレター, トレンド分析',
  },
  pricing: {
    title: '料金プラン',
    description: 'AICA-SySの料金プランをご確認ください。フリープラン、プレミアムプラン、エンタープライズプランからお選びいただけます。',
    keywords: '料金, プラン, 価格, サブスクリプション, フリー, プレミアム, エンタープライズ',
  },
  articles: {
    title: '技術記事一覧',
    description: 'TypeScriptエコシステムに関する高品質な技術記事を掲載しています。最新の技術動向、ベストプラクティス、チュートリアルをご提供します。',
    keywords: '技術記事, TypeScript, プログラミング, チュートリアル, ベストプラクティス, 技術動向',
  },
  newsletters: {
    title: 'ニュースレター一覧',
    description: 'TypeScriptエコシステムの最新情報をお届けするニュースレターです。週次・月次で技術動向、新機能、イベント情報を配信します。',
    keywords: 'ニュースレター, TypeScript, 技術情報, 週次, 月次, 配信, メールマガジン',
  },
  trends: {
    title: 'トレンド分析',
    description: 'TypeScriptエコシステムの最新トレンドをAIが分析し、可視化します。技術の流行、需要の変化、将来予測を提供します。',
    keywords: 'トレンド分析, TypeScript, 技術動向, 需要分析, 将来予測, データ可視化',
  },
  dashboard: {
    title: 'ダッシュボード',
    description: 'AICA-SySのダッシュボードで、コンテンツ管理、収益分析、ユーザー統計を確認できます。',
    keywords: 'ダッシュボード, 管理画面, 収益分析, ユーザー統計, コンテンツ管理',
  },
};

// 動的SEO設定生成
export function generateSEO(page: keyof typeof pageSEO, additionalProps?: Partial<NextSeoProps>): NextSeoProps {
  const pageConfig = pageSEO[page];
  
  return {
    ...defaultSEO,
    title: pageConfig.title,
    description: pageConfig.description,
    additionalMetaTags: [
      ...(defaultSEO.additionalMetaTags || []),
      {
        name: 'keywords',
        content: pageConfig.keywords,
      },
    ],
    ...additionalProps,
  };
}

// 記事用SEO設定
export function generateArticleSEO(article: {
  title: string;
  description: string;
  publishedTime: string;
  modifiedTime?: string;
  author: string;
  tags: string[];
  slug: string;
}): NextSeoProps {
  return {
    ...defaultSEO,
    title: article.title,
    description: article.description,
    canonical: `https://aica-sys.com/articles/${article.slug}`,
    openGraph: {
      ...defaultSEO.openGraph,
      title: article.title,
      description: article.description,
      type: 'article',
      article: {
        publishedTime: article.publishedTime,
        modifiedTime: article.modifiedTime || article.publishedTime,
        authors: [article.author],
        tags: article.tags,
      },
      url: `https://aica-sys.com/articles/${article.slug}`,
    },
    additionalMetaTags: [
      ...(defaultSEO.additionalMetaTags || []),
      {
        name: 'keywords',
        content: article.tags.join(', '),
      },
      {
        name: 'article:author',
        content: article.author,
      },
      {
        name: 'article:published_time',
        content: article.publishedTime,
      },
      {
        name: 'article:modified_time',
        content: article.modifiedTime || article.publishedTime,
      },
      {
        name: 'article:tag',
        content: article.tags.join(', '),
      },
    ],
  };
}

// 構造化データ生成
export function generateStructuredData(type: 'website' | 'article' | 'organization', data?: any) {
  const baseStructuredData = {
    '@context': 'https://schema.org',
  };

  switch (type) {
    case 'website':
      return {
        ...baseStructuredData,
        '@type': 'WebSite',
        name: 'AICA-SyS',
        description: 'AI-driven Content Curation & Automated Sales System',
        url: 'https://aica-sys.com',
        potentialAction: {
          '@type': 'SearchAction',
          target: 'https://aica-sys.com/search?q={search_term_string}',
          'query-input': 'required name=search_term_string',
        },
      };

    case 'article':
      return {
        ...baseStructuredData,
        '@type': 'Article',
        headline: data.title,
        description: data.description,
        author: {
          '@type': 'Person',
          name: data.author,
        },
        publisher: {
          '@type': 'Organization',
          name: 'AICA-SyS',
          logo: {
            '@type': 'ImageObject',
            url: 'https://aica-sys.com/logo.png',
          },
        },
        datePublished: data.publishedTime,
        dateModified: data.modifiedTime || data.publishedTime,
        mainEntityOfPage: {
          '@type': 'WebPage',
          '@id': `https://aica-sys.com/articles/${data.slug}`,
        },
      };

    case 'organization':
      return {
        ...baseStructuredData,
        '@type': 'Organization',
        name: 'AICA-SyS',
        description: 'AI-driven Content Curation & Automated Sales System',
        url: 'https://aica-sys.com',
        logo: 'https://aica-sys.com/logo.png',
        sameAs: [
          'https://twitter.com/aica_sys',
          'https://github.com/aica-sys',
        ],
      };

    default:
      return baseStructuredData;
  }
}
