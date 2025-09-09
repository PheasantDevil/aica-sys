'use client';

import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  ArrowRight,
  Calendar,
  Clock,
  Mail,
  Search,
  Star,
  Tag,
  Users,
} from 'lucide-react';
import { useState } from 'react';

export default function NewslettersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('all');

  // モックデータ（実際の実装ではAPIから取得）
  const newsletters = [
    {
      id: 1,
      title: 'TypeScript週間レポート #42',
      excerpt:
        '今週のTypeScriptエコシステムの動向、新機能、ベストプラクティスをまとめた週間レポートです。',
      type: 'weekly',
      publishedAt: '2024-09-08',
      readTime: '5分',
      subscribers: 1234,
      openRate: 68.5,
      clickRate: 12.3,
      tags: ['Weekly', 'TypeScript', 'Report'],
      featured: true,
    },
    {
      id: 2,
      title: 'Next.js 14新機能まとめ',
      excerpt:
        'Next.js 14で導入された新機能を詳しく解説し、実際のプロジェクトでの活用法を紹介します。',
      type: 'feature',
      publishedAt: '2024-09-07',
      readTime: '8分',
      subscribers: 1234,
      openRate: 72.1,
      clickRate: 15.8,
      tags: ['Next.js', 'React', 'Features'],
      featured: false,
    },
    {
      id: 3,
      title: 'React Server Components完全ガイド',
      excerpt:
        'React Server Componentsの概念から実装まで、パフォーマンス向上のための具体的な手法を紹介します。',
      type: 'tutorial',
      publishedAt: '2024-09-06',
      readTime: '12分',
      subscribers: 1234,
      openRate: 65.2,
      clickRate: 18.4,
      tags: ['React', 'Server Components', 'Tutorial'],
      featured: false,
    },
    {
      id: 4,
      title: 'TypeScript型安全性のベストプラクティス',
      excerpt:
        'TypeScriptでより安全なコードを書くための高度なテクニックとパターンを詳しく解説します。',
      type: 'best-practices',
      publishedAt: '2024-09-05',
      readTime: '6分',
      subscribers: 1234,
      openRate: 70.3,
      clickRate: 14.2,
      tags: ['TypeScript', 'Best Practices', 'Type Safety'],
      featured: false,
    },
    {
      id: 5,
      title: 'Vite vs Webpack: 2024年の比較',
      excerpt:
        'ViteとWebpackの最新の比較を行い、プロジェクトに最適なビルドツールの選び方を解説します。',
      type: 'comparison',
      publishedAt: '2024-09-04',
      readTime: '7分',
      subscribers: 1234,
      openRate: 63.8,
      clickRate: 11.7,
      tags: ['Vite', 'Webpack', 'Build Tools'],
      featured: false,
    },
  ];

  const types = [
    { id: 'all', name: 'すべて' },
    { id: 'weekly', name: '週間レポート' },
    { id: 'feature', name: '新機能紹介' },
    { id: 'tutorial', name: 'チュートリアル' },
    { id: 'best-practices', name: 'ベストプラクティス' },
    { id: 'comparison', name: '比較記事' },
  ];

  const getTypeBadge = (type: string) => {
    const colors = {
      weekly: 'bg-blue-100 text-blue-800',
      feature: 'bg-green-100 text-green-800',
      tutorial: 'bg-purple-100 text-purple-800',
      'best-practices': 'bg-orange-100 text-orange-800',
      comparison: 'bg-cyan-100 text-cyan-800',
    };
    return (
      <Badge
        className={
          colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800'
        }
      >
        {types.find(t => t.id === type)?.name || type}
      </Badge>
    );
  };

  const filteredNewsletters = newsletters.filter(newsletter => {
    const matchesSearch =
      newsletter.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      newsletter.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType =
      selectedType === 'all' || newsletter.type === selectedType;
    return matchesSearch && matchesType;
  });

  const featuredNewsletters = filteredNewsletters.filter(
    newsletter => newsletter.featured
  );
  const regularNewsletters = filteredNewsletters.filter(
    newsletter => !newsletter.featured
  );

  return (
    <div className='min-h-screen bg-background'>
      <Header />

      <main className='container py-8'>
        <div className='mb-8'>
          <h1 className='text-4xl font-bold text-foreground mb-4'>
            ニュースレター
          </h1>
          <p className='text-lg text-muted-foreground'>
            TypeScriptエコシステムの最新情報をお届けします
          </p>
        </div>

        {/* 検索・フィルター */}
        <Card className='mb-8'>
          <CardContent className='pt-6'>
            <div className='flex flex-col lg:flex-row gap-4'>
              <div className='relative flex-1'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
                <Input
                  placeholder='ニュースレターを検索...'
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className='pl-10'
                />
              </div>
              <div className='flex gap-2'>
                <select
                  value={selectedType}
                  onChange={e => setSelectedType(e.target.value)}
                  className='px-3 py-2 border border-input bg-background rounded-md text-sm'
                >
                  {types.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* おすすめニュースレター */}
        {featuredNewsletters.length > 0 && (
          <div className='mb-12'>
            <h2 className='text-2xl font-bold text-foreground mb-6'>
              おすすめニュースレター
            </h2>
            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              {featuredNewsletters.map(newsletter => (
                <Card
                  key={newsletter.id}
                  className='border-primary bg-primary/5'
                >
                  <CardHeader>
                    <div className='flex items-center justify-between mb-2'>
                      {getTypeBadge(newsletter.type)}
                      <Badge className='bg-yellow-100 text-yellow-800'>
                        おすすめ
                      </Badge>
                    </div>
                    <CardTitle className='text-xl'>
                      {newsletter.title}
                    </CardTitle>
                    <CardDescription className='text-base'>
                      {newsletter.excerpt}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className='flex items-center justify-between text-sm text-muted-foreground mb-4'>
                      <div className='flex items-center gap-4'>
                        <div className='flex items-center gap-1'>
                          <Calendar className='h-4 w-4' />
                          {newsletter.publishedAt}
                        </div>
                        <div className='flex items-center gap-1'>
                          <Clock className='h-4 w-4' />
                          {newsletter.readTime}
                        </div>
                      </div>
                    </div>
                    <div className='grid grid-cols-3 gap-4 text-sm text-muted-foreground mb-4'>
                      <div className='flex items-center gap-1'>
                        <Users className='h-4 w-4' />
                        {newsletter.subscribers.toLocaleString()}
                      </div>
                      <div className='flex items-center gap-1'>
                        <Mail className='h-4 w-4' />
                        {newsletter.openRate}%
                      </div>
                      <div className='flex items-center gap-1'>
                        <Star className='h-4 w-4' />
                        {newsletter.clickRate}%
                      </div>
                    </div>
                    <div className='flex items-center justify-between'>
                      <div className='flex flex-wrap gap-2'>
                        {newsletter.tags.map(tag => (
                          <Badge
                            key={tag}
                            variant='outline'
                            className='text-xs'
                          >
                            <Tag className='h-3 w-3 mr-1' />
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <Button className='flex items-center gap-2'>
                        読む
                        <ArrowRight className='h-4 w-4' />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* 通常ニュースレター */}
        <div>
          <h2 className='text-2xl font-bold text-foreground mb-6'>
            {featuredNewsletters.length > 0
              ? 'その他のニュースレター'
              : 'ニュースレター一覧'}
          </h2>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {regularNewsletters.map(newsletter => (
              <Card
                key={newsletter.id}
                className='hover:shadow-lg transition-shadow'
              >
                <CardHeader>
                  <div className='flex items-center justify-between mb-2'>
                    {getTypeBadge(newsletter.type)}
                  </div>
                  <CardTitle className='text-lg line-clamp-2'>
                    {newsletter.title}
                  </CardTitle>
                  <CardDescription className='line-clamp-3'>
                    {newsletter.excerpt}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='flex items-center justify-between text-sm text-muted-foreground mb-4'>
                    <div className='flex items-center gap-3'>
                      <div className='flex items-center gap-1'>
                        <Calendar className='h-4 w-4' />
                        {newsletter.publishedAt}
                      </div>
                      <div className='flex items-center gap-1'>
                        <Clock className='h-4 w-4' />
                        {newsletter.readTime}
                      </div>
                    </div>
                  </div>
                  <div className='grid grid-cols-3 gap-2 text-xs text-muted-foreground mb-4'>
                    <div className='text-center'>
                      <div className='font-medium'>
                        {newsletter.subscribers.toLocaleString()}
                      </div>
                      <div>購読者</div>
                    </div>
                    <div className='text-center'>
                      <div className='font-medium'>{newsletter.openRate}%</div>
                      <div>開封率</div>
                    </div>
                    <div className='text-center'>
                      <div className='font-medium'>{newsletter.clickRate}%</div>
                      <div>クリック率</div>
                    </div>
                  </div>
                  <div className='flex items-center justify-between'>
                    <div className='flex flex-wrap gap-1'>
                      {newsletter.tags.slice(0, 2).map(tag => (
                        <Badge key={tag} variant='outline' className='text-xs'>
                          {tag}
                        </Badge>
                      ))}
                      {newsletter.tags.length > 2 && (
                        <Badge variant='outline' className='text-xs'>
                          +{newsletter.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                    <Button size='sm' className='flex items-center gap-1'>
                      読む
                      <ArrowRight className='h-3 w-3' />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {filteredNewsletters.length === 0 && (
          <Card>
            <CardContent className='pt-6 text-center'>
              <p className='text-muted-foreground mb-4'>
                条件に一致するニュースレターが見つかりませんでした
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedType('all');
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
