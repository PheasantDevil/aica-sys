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
import { Badge } from '@/components/ui/badge';
import {
  TrendingUp,
  TrendingDown,
  Calendar,
  BarChart3,
  Star,
  GitBranch,
  Download,
  ExternalLink,
} from 'lucide-react';
import { useState } from 'react';

export default function TrendsPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // モックデータ（実際の実装ではAPIから取得）
  const trends = [
    {
      id: 1,
      title: 'TypeScript 5.0',
      category: 'TypeScript',
      description: '最新のTypeScriptバージョンが急速に普及',
      trend: 'up',
      change: 45.2,
      stars: 12500,
      downloads: 2340000,
      period: 'week',
      tags: ['TypeScript', 'Compiler', 'Type Safety'],
      featured: true,
    },
    {
      id: 2,
      title: 'Next.js 14 App Router',
      category: 'Framework',
      description: 'App Routerの採用率が大幅に増加',
      trend: 'up',
      change: 32.8,
      stars: 8900,
      downloads: 1870000,
      period: 'week',
      tags: ['Next.js', 'React', 'App Router'],
      featured: true,
    },
    {
      id: 3,
      title: 'React Server Components',
      category: 'React',
      description: 'Server Componentsの実装が本格化',
      trend: 'up',
      change: 28.5,
      stars: 5600,
      downloads: 1200000,
      period: 'week',
      tags: ['React', 'Server Components', 'Performance'],
      featured: false,
    },
    {
      id: 4,
      title: 'Vite 5.0',
      category: 'Build Tools',
      description: 'Viteの新バージョンが注目を集める',
      trend: 'up',
      change: 22.1,
      stars: 7800,
      downloads: 1560000,
      period: 'week',
      tags: ['Vite', 'Build Tools', 'Performance'],
      featured: false,
    },
    {
      id: 5,
      title: 'Webpack 5',
      category: 'Build Tools',
      description: 'Webpack 5の採用率が減少傾向',
      trend: 'down',
      change: -15.3,
      stars: 4500,
      downloads: 980000,
      period: 'week',
      tags: ['Webpack', 'Build Tools', 'Legacy'],
      featured: false,
    },
  ];

  const categories = [
    { id: 'all', name: 'すべて' },
    { id: 'TypeScript', name: 'TypeScript' },
    { id: 'Framework', name: 'フレームワーク' },
    { id: 'React', name: 'React' },
    { id: 'Build Tools', name: 'ビルドツール' },
  ];

  const periods = [
    { id: 'week', name: '1週間' },
    { id: 'month', name: '1ヶ月' },
    { id: 'quarter', name: '3ヶ月' },
  ];

  const getCategoryBadge = (category: string) => {
    const colors = {
      TypeScript: 'bg-blue-100 text-blue-800',
      Framework: 'bg-green-100 text-green-800',
      React: 'bg-cyan-100 text-cyan-800',
      'Build Tools': 'bg-purple-100 text-purple-800',
    };
    return (
      <Badge className={colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
        {category}
      </Badge>
    );
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') {
      return <TrendingUp className='h-4 w-4 text-green-600' />;
    } else if (trend === 'down') {
      return <TrendingDown className='h-4 w-4 text-red-600' />;
    }
    return null;
  };

  const getTrendColor = (trend: string, change: number) => {
    if (trend === 'up') {
      return 'text-green-600';
    } else if (trend === 'down') {
      return 'text-red-600';
    }
    return 'text-muted-foreground';
  };

  const filteredTrends = trends.filter(trend => {
    const matchesCategory = selectedCategory === 'all' || trend.category === selectedCategory;
    const matchesPeriod = trend.period === selectedPeriod;
    return matchesCategory && matchesPeriod;
  });

  const featuredTrends = filteredTrends.filter(trend => trend.featured);
  const regularTrends = filteredTrends.filter(trend => !trend.featured);

  return (
    <div className='min-h-screen bg-background'>
      <Header />

      <main className='container py-8'>
        <div className='mb-8'>
          <h1 className='text-4xl font-bold text-foreground mb-4'>トレンド分析</h1>
          <p className='text-lg text-muted-foreground'>
            TypeScriptエコシステムの最新動向とトレンドを分析
          </p>
        </div>

        {/* フィルター */}
        <Card className='mb-8'>
          <CardContent className='pt-6'>
            <div className='flex flex-col lg:flex-row gap-4'>
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
                  value={selectedPeriod}
                  onChange={e => setSelectedPeriod(e.target.value)}
                  className='px-3 py-2 border border-input bg-background rounded-md text-sm'
                >
                  {periods.map(period => (
                    <option key={period.id} value={period.id}>
                      {period.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className='flex-1' />
              <Button>
                <Download className='mr-2 h-4 w-4' />
                レポートをダウンロード
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* おすすめトレンド */}
        {featuredTrends.length > 0 && (
          <div className='mb-12'>
            <h2 className='text-2xl font-bold text-foreground mb-6'>注目のトレンド</h2>
            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              {featuredTrends.map(trend => (
                <Card key={trend.id} className='border-primary bg-primary/5'>
                  <CardHeader>
                    <div className='flex items-center justify-between mb-2'>
                      {getCategoryBadge(trend.category)}
                      <Badge className='bg-yellow-100 text-yellow-800'>注目</Badge>
                    </div>
                    <CardTitle className='text-xl'>{trend.title}</CardTitle>
                    <CardDescription className='text-base'>
                      {trend.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className='flex items-center justify-between mb-4'>
                      <div className='flex items-center gap-2'>
                        {getTrendIcon(trend.trend)}
                        <span className={`text-lg font-semibold ${getTrendColor(trend.trend, trend.change)}`}>
                          {trend.change > 0 ? '+' : ''}{trend.change}%
                        </span>
                      </div>
                      <div className='text-sm text-muted-foreground'>
                        {selectedPeriod === 'week' ? '1週間' : selectedPeriod === 'month' ? '1ヶ月' : '3ヶ月'}の変化
                      </div>
                    </div>
                    
                    <div className='grid grid-cols-2 gap-4 text-sm text-muted-foreground mb-4'>
                      <div className='flex items-center gap-2'>
                        <Star className='h-4 w-4' />
                        {trend.stars.toLocaleString()} stars
                      </div>
                      <div className='flex items-center gap-2'>
                        <Download className='h-4 w-4' />
                        {trend.downloads.toLocaleString()} downloads
                      </div>
                    </div>

                    <div className='flex items-center justify-between'>
                      <div className='flex flex-wrap gap-2'>
                        {trend.tags.map(tag => (
                          <Badge key={tag} variant='outline' className='text-xs'>
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <Button size='sm' className='flex items-center gap-1'>
                        詳細を見る
                        <ExternalLink className='h-3 w-3' />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* 通常トレンド */}
        <div>
          <h2 className='text-2xl font-bold text-foreground mb-6'>
            {featuredTrends.length > 0 ? 'その他のトレンド' : 'トレンド一覧'}
          </h2>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>
            {regularTrends.map(trend => (
              <Card key={trend.id} className='hover:shadow-lg transition-shadow'>
                <CardHeader>
                  <div className='flex items-center justify-between mb-2'>
                    {getCategoryBadge(trend.category)}
                  </div>
                  <CardTitle className='text-lg line-clamp-2'>{trend.title}</CardTitle>
                  <CardDescription className='line-clamp-2'>
                    {trend.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='flex items-center justify-between mb-4'>
                    <div className='flex items-center gap-2'>
                      {getTrendIcon(trend.trend)}
                      <span className={`text-lg font-semibold ${getTrendColor(trend.trend, trend.change)}`}>
                        {trend.change > 0 ? '+' : ''}{trend.change}%
                      </span>
                    </div>
                  </div>
                  
                  <div className='grid grid-cols-2 gap-2 text-xs text-muted-foreground mb-4'>
                    <div className='text-center'>
                      <div className='font-medium'>{trend.stars.toLocaleString()}</div>
                      <div>stars</div>
                    </div>
                    <div className='text-center'>
                      <div className='font-medium'>{trend.downloads.toLocaleString()}</div>
                      <div>downloads</div>
                    </div>
                  </div>

                  <div className='flex items-center justify-between'>
                    <div className='flex flex-wrap gap-1'>
                      {trend.tags.slice(0, 2).map(tag => (
                        <Badge key={tag} variant='outline' className='text-xs'>
                          {tag}
                        </Badge>
                      ))}
                      {trend.tags.length > 2 && (
                        <Badge variant='outline' className='text-xs'>
                          +{trend.tags.length - 2}
                        </Badge>
                      )}
                    </div>
                    <Button size='sm' className='flex items-center gap-1'>
                      詳細
                      <ExternalLink className='h-3 w-3' />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {filteredTrends.length === 0 && (
          <Card>
            <CardContent className='pt-6 text-center'>
              <p className='text-muted-foreground mb-4'>
                条件に一致するトレンドが見つかりませんでした
              </p>
              <Button
                onClick={() => {
                  setSelectedCategory('all');
                  setSelectedPeriod('week');
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
