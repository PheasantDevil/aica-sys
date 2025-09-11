'use client';

import { useQuery } from '@tanstack/react-query';

interface Trend {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  publishedAt: string;
  trendScore: number;
  changeRate: number;
  engagement: number;
  isPremium: boolean;
  imageUrl?: string;
  metrics: {
    mentions: number;
    growth: number;
    sentiment: 'positive' | 'neutral' | 'negative';
  };
}

interface Filters {
  timeframe: string;
  category: string;
  sortBy: string;
}

export function useTrends(filters: Filters) {
  return useQuery({
    queryKey: ['trends', filters],
    queryFn: async (): Promise<Trend[]> => {
      const params = new URLSearchParams();
      if (filters.timeframe) params.append('timeframe', filters.timeframe);
      if (filters.category !== 'all') params.append('category', filters.category);
      if (filters.sortBy) params.append('sortBy', filters.sortBy);

      const response = await fetch(`/api/trends?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch trends');
      }
      return response.json();
    },
    // モックデータを返す（実際の実装ではAPIから取得）
    placeholderData: () => [
      {
        id: '1',
        title: 'TypeScript 5.0の採用率が急上昇',
        description: 'TypeScript 5.0のリリースから1ヶ月で、主要プロジェクトでの採用率が前月比150%増加。新機能のconst assertionsとtemplate literal typesが特に人気。',
        category: 'ecosystem',
        tags: ['TypeScript', '5.0', 'Adoption', 'Growth'],
        publishedAt: '2024-01-15T10:00:00Z',
        trendScore: 95,
        changeRate: 150,
        engagement: 87,
        isPremium: false,
        imageUrl: '/images/typescript-5-0-adoption.jpg',
        metrics: {
          mentions: 1247,
          growth: 150,
          sentiment: 'positive',
        },
      },
      {
        id: '2',
        title: 'Next.js 14とTypeScriptの組み合わせが主流に',
        description: 'Next.js 14のApp RouterとTypeScriptの組み合わせが、フルスタック開発の新たな標準として急速に普及。開発者体験の向上が主な要因。',
        category: 'frameworks',
        tags: ['Next.js', 'TypeScript', 'Full Stack', 'App Router'],
        publishedAt: '2024-01-14T14:30:00Z',
        trendScore: 88,
        changeRate: 89,
        engagement: 92,
        isPremium: true,
        imageUrl: '/images/nextjs-typescript-trend.jpg',
        metrics: {
          mentions: 892,
          growth: 89,
          sentiment: 'positive',
        },
      },
      {
        id: '3',
        title: 'Zodライブラリの使用率が爆発的に増加',
        description: 'TypeScriptの型安全性をランタイムでも実現するZodライブラリの使用率が、過去3ヶ月で300%増加。APIバリデーションでの採用が特に顕著。',
        category: 'libraries',
        tags: ['Zod', 'TypeScript', 'Validation', 'Runtime Safety'],
        publishedAt: '2024-01-13T09:15:00Z',
        trendScore: 82,
        changeRate: 300,
        engagement: 78,
        isPremium: false,
        imageUrl: '/images/zod-trend.jpg',
        metrics: {
          mentions: 654,
          growth: 300,
          sentiment: 'positive',
        },
      },
      {
        id: '4',
        title: 'React 18のConcurrent FeaturesとTypeScript',
        description: 'React 18のConcurrent FeaturesをTypeScriptで活用するパターンが確立されつつある。SuspenseとError Boundariesの型安全性が注目の的。',
        category: 'frameworks',
        tags: ['React', 'TypeScript', 'Concurrent Features', 'Suspense'],
        publishedAt: '2024-01-12T16:45:00Z',
        trendScore: 76,
        changeRate: 45,
        engagement: 85,
        isPremium: true,
        imageUrl: '/images/react-concurrent-typescript.jpg',
        metrics: {
          mentions: 423,
          growth: 45,
          sentiment: 'positive',
        },
      },
      {
        id: '5',
        title: 'TypeScriptの型操作テクニックが進化',
        description: 'Template Literal TypesやConditional Typesを使った高度な型操作テクニックが、ライブラリ開発者を中心に急速に普及。型レベルプログラミングの新時代。',
        category: 'patterns',
        tags: ['TypeScript', 'Type Manipulation', 'Advanced', 'Template Literal Types'],
        publishedAt: '2024-01-11T11:20:00Z',
        trendScore: 71,
        changeRate: 67,
        engagement: 73,
        isPremium: false,
        imageUrl: '/images/typescript-type-manipulation.jpg',
        metrics: {
          mentions: 312,
          growth: 67,
          sentiment: 'neutral',
        },
      },
      {
        id: '6',
        title: 'ViteとTypeScriptの組み合わせが人気',
        description: 'Viteの高速な開発サーバーとTypeScriptの組み合わせが、モダンフロントエンド開発の新たな選択肢として注目。ビルド時間の短縮が主な利点。',
        category: 'tools',
        tags: ['Vite', 'TypeScript', 'Build Tool', 'Development'],
        publishedAt: '2024-01-10T13:10:00Z',
        trendScore: 68,
        changeRate: 34,
        engagement: 69,
        isPremium: false,
        imageUrl: '/images/vite-typescript.jpg',
        metrics: {
          mentions: 198,
          growth: 34,
          sentiment: 'positive',
        },
      },
    ],
  });
}
