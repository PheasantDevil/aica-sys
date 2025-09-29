'use client';

import { apiClient } from '@/lib/api-client';
import { useQuery } from '@tanstack/react-query';

interface Newsletter {
  id: string;
  title: string;
  description: string;
  content: string;
  publishedAt: string;
  subscribers: number;
  openRate: number;
  clickRate: number;
  isPremium: boolean;
  imageUrl?: string;
  tags: string[];
}

export function useNewsletters() {
  const query = useQuery({
    queryKey: ['newsletters'],
    queryFn: async (): Promise<Newsletter[]> => {
      const response = await apiClient.getNewsletters();

      if (response.error) {
        throw new Error(response.error);
      }

      return response.data?.newsletters || [];
    },
    // モックデータを返す（実際の実装ではAPIから取得）
    placeholderData: () => [
      {
        id: '1',
        title: '週刊TypeScriptニュース #42',
        description:
          '今週のTypeScriptエコシステムの重要なアップデートをお届けします。新機能、ライブラリの更新、コミュニティの動向をまとめました。',
        content: '',
        publishedAt: '2024-01-15T09:00:00Z',
        subscribers: 2341,
        openRate: 78,
        clickRate: 23,
        isPremium: false,
        imageUrl: '/images/newsletter-42.jpg',
        tags: ['TypeScript', 'Weekly', 'News', 'Update'],
      },
      {
        id: '2',
        title: 'TypeScript 5.0リリース記念特別号',
        description:
          'TypeScript 5.0の正式リリースを記念して、新機能の詳細解説と移行ガイドをお届けします。',
        content: '',
        publishedAt: '2024-01-12T14:30:00Z',
        subscribers: 2341,
        openRate: 85,
        clickRate: 31,
        isPremium: true,
        imageUrl: '/images/typescript-5-0-special.jpg',
        tags: ['TypeScript', 'Release', 'Special', '5.0'],
      },
      {
        id: '3',
        title: 'React 18とTypeScriptの組み合わせ',
        description:
          'React 18の新機能をTypeScriptと組み合わせて使用する際のベストプラクティスを紹介します。',
        content: '',
        publishedAt: '2024-01-10T11:15:00Z',
        subscribers: 2341,
        openRate: 72,
        clickRate: 19,
        isPremium: false,
        imageUrl: '/images/react-typescript-newsletter.jpg',
        tags: ['React', 'TypeScript', 'Best Practices', 'Tutorial'],
      },
      {
        id: '4',
        title: 'Next.js 14の新機能とTypeScript',
        description:
          'Next.js 14で追加された新機能をTypeScriptで活用する方法を詳しく解説します。',
        content: '',
        publishedAt: '2024-01-08T16:45:00Z',
        subscribers: 2341,
        openRate: 81,
        clickRate: 27,
        isPremium: true,
        imageUrl: '/images/nextjs-14-typescript.jpg',
        tags: ['Next.js', 'TypeScript', 'New Features', 'Tutorial'],
      },
      {
        id: '5',
        title: 'TypeScriptの型安全性を高めるテクニック',
        description:
          'TypeScriptの型システムを最大限活用して、より安全なコードを書くための実践的なテクニックを紹介します。',
        content: '',
        publishedAt: '2024-01-05T10:20:00Z',
        subscribers: 2341,
        openRate: 76,
        clickRate: 22,
        isPremium: false,
        imageUrl: '/images/typescript-safety-tips.jpg',
        tags: ['TypeScript', 'Type Safety', 'Tips', 'Best Practices'],
      },
      {
        id: '6',
        title: '2024年TypeScriptエコシステムの展望',
        description:
          '2024年のTypeScriptエコシステムの主要なトレンドと今後の展望について詳しく分析します。',
        content: '',
        publishedAt: '2024-01-03T13:30:00Z',
        subscribers: 2341,
        openRate: 83,
        clickRate: 29,
        isPremium: true,
        imageUrl: '/images/typescript-2024-outlook.jpg',
        tags: ['TypeScript', '2024', 'Trends', 'Analysis'],
      },
    ],
  });

  return {
    newsletters: query.data || [],
    isLoading: query.isLoading,
    error: query.error,
  };
}
