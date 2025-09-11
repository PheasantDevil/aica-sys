'use client';

import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';

interface Article {
  id: string;
  title: string;
  description: string;
  content: string;
  author: {
    name: string;
    avatar?: string;
  };
  category: string;
  tags: string[];
  publishedAt: string;
  readTime: number;
  views: number;
  likes: number;
  isPremium: boolean;
  imageUrl?: string;
}

interface Filters {
  category: string;
  sortBy: string;
  search: string;
}

export function useArticles(filters: Filters) {
  const { data: session } = useSession();

  return useQuery({
    queryKey: ['articles', filters],
    queryFn: async (): Promise<Article[]> => {
      const params = new URLSearchParams();
      if (filters.category !== 'all') params.append('category', filters.category);
      if (filters.sortBy) params.append('sortBy', filters.sortBy);
      if (filters.search) params.append('search', filters.search);

      const response = await fetch(`/api/articles?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch articles');
      }
      return response.json();
    },
    // モックデータを返す（実際の実装ではAPIから取得）
    placeholderData: () => [
      {
        id: '1',
        title: 'TypeScript 5.0の新機能とベストプラクティス',
        description: '最新のTypeScript 5.0で追加された新機能について詳しく解説します。const assertions、template literal types、そして新しいコンパイラオプションについて学びましょう。',
        content: '',
        author: {
          name: '田中太郎',
          avatar: '/avatars/tanaka.jpg',
        },
        category: 'tutorial',
        tags: ['TypeScript', 'JavaScript', 'Tutorial', 'New Features'],
        publishedAt: '2024-01-15T10:00:00Z',
        readTime: 8,
        views: 1234,
        likes: 89,
        isPremium: false,
        imageUrl: '/images/typescript-5-0.jpg',
      },
      {
        id: '2',
        title: 'React 18とTypeScriptの完全ガイド',
        description: 'React 18の新機能をTypeScriptと組み合わせて使用する方法を詳しく解説します。Concurrent Features、Suspense、そして新しいHooksについて学びましょう。',
        content: '',
        author: {
          name: '佐藤花子',
          avatar: '/avatars/sato.jpg',
        },
        category: 'tutorial',
        tags: ['React', 'TypeScript', 'JavaScript', 'Frontend'],
        publishedAt: '2024-01-14T14:30:00Z',
        readTime: 12,
        views: 2156,
        likes: 156,
        isPremium: true,
        imageUrl: '/images/react-18-typescript.jpg',
      },
      {
        id: '3',
        title: 'TypeScriptの型安全性を最大化する10のテクニック',
        description: 'TypeScriptの型システムを最大限活用して、より安全で保守しやすいコードを書くための実践的なテクニックを紹介します。',
        content: '',
        author: {
          name: '山田次郎',
          avatar: '/avatars/yamada.jpg',
        },
        category: 'tips',
        tags: ['TypeScript', 'Type Safety', 'Best Practices', 'Tips'],
        publishedAt: '2024-01-13T09:15:00Z',
        readTime: 6,
        views: 987,
        likes: 67,
        isPremium: false,
        imageUrl: '/images/typescript-tips.jpg',
      },
      {
        id: '4',
        title: 'Next.js 14とTypeScriptで作るフルスタックアプリ',
        description: 'Next.js 14の最新機能とTypeScriptを組み合わせて、本格的なフルスタックアプリケーションを構築する方法をステップバイステップで解説します。',
        content: '',
        author: {
          name: '鈴木一郎',
          avatar: '/avatars/suzuki.jpg',
        },
        category: 'tutorial',
        tags: ['Next.js', 'TypeScript', 'Full Stack', 'Tutorial'],
        publishedAt: '2024-01-12T16:45:00Z',
        readTime: 15,
        views: 3456,
        likes: 234,
        isPremium: true,
        imageUrl: '/images/nextjs-typescript.jpg',
      },
      {
        id: '5',
        title: 'TypeScript 4.9から5.0への移行ガイド',
        description: 'TypeScript 4.9から5.0への移行時に注意すべき点と、新機能を活用するための移行戦略について詳しく解説します。',
        content: '',
        author: {
          name: '高橋美咲',
          avatar: '/avatars/takahashi.jpg',
        },
        category: 'news',
        tags: ['TypeScript', 'Migration', 'Update', 'News'],
        publishedAt: '2024-01-11T11:20:00Z',
        readTime: 10,
        views: 1876,
        likes: 123,
        isPremium: false,
        imageUrl: '/images/typescript-migration.jpg',
      },
      {
        id: '6',
        title: 'TypeScriptの高度な型操作テクニック',
        description: 'TypeScriptの条件型、マッピング型、テンプレートリテラル型などの高度な型操作テクニックを実例とともに詳しく解説します。',
        content: '',
        author: {
          name: '伊藤健太',
          avatar: '/avatars/ito.jpg',
        },
        category: 'advanced',
        tags: ['TypeScript', 'Advanced', 'Type Manipulation', 'Expert'],
        publishedAt: '2024-01-10T13:10:00Z',
        readTime: 18,
        views: 987,
        likes: 78,
        isPremium: true,
        imageUrl: '/images/advanced-typescript.jpg',
      },
    ],
  });
}
