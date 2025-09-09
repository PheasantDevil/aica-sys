'use client';

import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Search,
  Filter,
  Calendar,
  Eye,
  Star,
  Clock,
  User,
  Tag,
} from 'lucide-react';
import { useState } from 'react';

export default function ArticlesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('newest');

  // モックデータ（実際の実装ではAPIから取得）
  const articles = [
    {
      id: 1,
      title: 'TypeScript 5.0の新機能とベストプラクティス',
      excerpt: 'TypeScript 5.0で導入された新機能を詳しく解説し、実際のプロジェクトでの活用法を紹介します。',
      author: 'AICA Team',
      publishedAt: '2024-09-08',
      readTime: '8分',
      views: 1234,
      likes: 89,
      category: 'TypeScript',
      tags: ['TypeScript', 'JavaScript', 'Tutorial'],
      featured: true,
    },
    {
      id: 2,
      title: 'Next.js 14 App Router完全ガイド',
      excerpt: 'Next.js 14のApp Routerの基本から応用まで、実践的な使い方をステップバイステップで解説します。',
      author: 'AICA Team',
      publishedAt: '2024-09-07',
      readTime: '12分',
      views: 987,
      likes: 67,
      category: 'Next.js',
      tags: ['Next.js', 'React', 'Tutorial'],
      featured: false,
    },
    {
      id: 3,
      title: 'React Server Componentsの実践的活用法',
      excerpt: 'React Server Componentsの概念から実装まで、パフォーマンス向上のための具体的な手法を紹介します。',
      author: 'AICA Team',
      publishedAt: '2024-09-06',
      readTime: '10分',
      views: 756,
      likes: 45,
      category: 'React',
      tags: ['React', 'Server Components', 'Performance'],
      featured: false,
    },
    {
      id: 4,
      title: 'TypeScript型安全性の向上テクニック',
      excerpt: 'TypeScriptでより安全なコードを書くための高度なテクニックとパターンを詳しく解説します。',
      author: 'AICA Team',
      publishedAt: '2024-09-05',
      readTime: '6分',
      views: 543,
      likes: 32,
      category: 'TypeScript',
      tags: ['TypeScript', 'Type Safety', 'Best Practices'],
      featured: false,
    },
    {
      id: 5,
      title: 'Vite vs Webpack: 2024年の比較',
      excerpt: 'ViteとWebpackの最新の比較を行い、プロジェクトに最適なビルドツールの選び方を解説します。',
      author: 'AICA Team',
      publishedAt: '2024-09-04',
      readTime: '7分',
      views: 432,
      likes: 28,
      category: 'Build Tools',
      tags: ['Vite', 'Webpack', 'Build Tools'],
      featured: false,
    },
  ];

  const categories = [
    { id: 'all', name: 'すべて' },
    { id: 'TypeScript', name: 'TypeScript' },
    { id: 'Next.js', name: 'Next.js' },
    { id: 'React', name: 'React' },
    { id: 'Build Tools', name: 'Build Tools' },
  ];

  const sortOptions = [
    { id: 'newest', name: '最新順' },
    { id: 'popular', name: '人気順' },
    { id: 'views', name: '閲覧数順' },
    { id: 'likes', name: 'いいね順' },
  ];

  const getCategoryBadge = (category: string) => {
    const colors = {
      TypeScript: 'bg-blue-100 text-blue-800',
      'Next.js': 'bg-green-100 text-green-800',
      React: 'bg-cyan-100 text-cyan-800',
      'Build Tools': 'bg-purple-100 text-purple-800',
    };
    return (
      <Badge className={colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {category}
      </Badge>
    );
  };

  const filteredAndSortedArticles = articles
    .filter(article => {
      const matchesSearch = article.title
        .toLowerCase()
        .includes(searchQuery.toLowerCase()) ||
        article.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
        case 'popular':
          return b.views - a.views;
        case 'views':
          return b.views - a.views;
        case 'likes':
          return b.likes - a.likes;
        default:
          return 0;
      }
    });

  const featuredArticles = filteredAndSortedArticles.filter(article => article.featured);
  const regularArticles = filteredAndSortedArticles.filter(article => !article.featured);

  return (
    <div className='min-h-screen bg-background'>
      <Header />

      <main className='container py-8'>
        <div className='mb-8'>
          <h1 className='text-4xl font-bold text-foreground mb-4'>記事一覧</h1>
          <p className='text-lg text-muted-foreground'>
            TypeScriptエコシステムの最新情報とベストプラクティス
          </p>
        </div>

        {/* 検索・フィルター */}
        <Card className='mb-8'>
          <CardContent className='pt-6'>
            <div className='flex flex-col lg:flex-row gap-4'>
              <div className='relative flex-1'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
                <Input
                  placeholder='記事を検索...'
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className='pl-10'
                />
              </div>
              <div className='flex gap-2'>
                <select
                  value={selectedCategory}
                  onChange={e => setSelectedCategory(e.target.value)}
                  className='px-3 py-2 border border-input bg-background rounded-md text-sm'
                >
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value)}
                  className='px-3 py-2 border border-input bg-background rounded-md text-sm'
                >
                  {sortOptions.map(option => (
                    <option key={option.id} value={option.id}>
                      {option.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* おすすめ記事 */}
        {featuredArticles.length > 0 && (
          <div className='mb-12'>
            <h2 className='text-2xl font-bold text-foreground mb-6'>おすすめ記事</h2>
            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              {featuredArticles.map(article => (
                <Card key={article.id} className='border-primary bg-primary/5'>
                  <CardHeader>
                    <div className='flex items-center justify-between mb-2'>
                      {getCategoryBadge(article.category)}
                      <Badge className='bg-yellow-100 text-yellow-800'>おすすめ</Badge>
                    </div>
                    <CardTitle className='text-xl'>{article.title}</CardTitle>
                    <CardDescription className='text-base'>
                      {article.excerpt}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className='flex items-center justify-between text-sm text-muted-foreground mb-4'>
                      <div className='flex items-center gap-4'>
                        <div className='flex items-center gap-1'>
                          <User className='h-4 w-4' />
                          {article.author}
                        </div>
                        <div className='flex items-center gap-1'>
                          <Calendar className='h-4 w-4' />
                          {article.publishedAt}
                        </div>
                        <div className='flex items-center gap-1'>
                          <Clock className='h-4 w-4' />
                          {article.readTime}
                        </div>
                      </div>
                    </div>
                    <div className='flex items-center justify-between'>
                      <div className='flex items-center gap-4 text-sm text-muted-foreground'>
                        <div className='flex items-center gap-1'>
                          <Eye className='h-4 w-4' />
                          {article.views.toLocaleString()}
                        </div>
                        <div className='flex items-center gap-1'>
                          <Star className='h-4 w-4' />
                          {article.likes}
                        </div>
                      </div>
                      <Button>記事を読む</Button>
                    </div>
                    <div className='flex flex-wrap gap-2 mt-4'>
                      {article.tags.map(tag => (
                        <Badge key={tag} variant='outline' className='text-xs'>
                          <Tag className='h-3 w-3 mr-1' />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* 通常記事 */}
        <div>
          <h2 className='text-2xl font-bold text-foreground mb-6'>
            {featuredArticles.length > 0 ? 'その他の記事' : '記事一覧'}
          </h2>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {regularArticles.map(article => (
              <Card key={article.id} className='hover:shadow-lg transition-shadow'>
                <CardHeader>
                  <div className='flex items-center justify-between mb-2'>
                    {getCategoryBadge(article.category)}
                  </div>
                  <CardTitle className='text-lg line-clamp-2'>{article.title}</CardTitle>
                  <CardDescription className='line-clamp-3'>
                    {article.excerpt}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='flex items-center justify-between text-sm text-muted-foreground mb-4'>
                    <div className='flex items-center gap-3'>
                      <div className='flex items-center gap-1'>
                        <Calendar className='h-4 w-4' />
                        {article.publishedAt}
                      </div>
                      <div className='flex items-center gap-1'>
                        <Clock className='h-4 w-4' />
                        {article.readTime}
                      </div>
                    </div>
                  </div>
                  <div className='flex items-center justify-between mb-4'>
                    <div className='flex items-center gap-4 text-sm text-muted-foreground'>
                      <div className='flex items-center gap-1'>
                        <Eye className='h-4 w-4' />
                        {article.views.toLocaleString()}
                      </div>
                      <div className='flex items-center gap-1'>
                        <Star className='h-4 w-4' />
                        {article.likes}
                      </div>
                    </div>
                    <Button size='sm'>読む</Button>
                  </div>
                  <div className='flex flex-wrap gap-1'>
                    {article.tags.slice(0, 3).map(tag => (
                      <Badge key={tag} variant='outline' className='text-xs'>
                        {tag}
                      </Badge>
                    ))}
                    {article.tags.length > 3 && (
                      <Badge variant='outline' className='text-xs'>
                        +{article.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {filteredAndSortedArticles.length === 0 && (
          <Card>
            <CardContent className='pt-6 text-center'>
              <p className='text-muted-foreground mb-4'>
                条件に一致する記事が見つかりませんでした
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                }}
              >
                フィルターをリセット
              </Button>
            </CardContent>
          </Card>
        )}
      </main>

      <Footer />
    </div>
  );
}
