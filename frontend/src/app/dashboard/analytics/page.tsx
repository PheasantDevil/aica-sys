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
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Eye,
  Star,
  Mail,
  Calendar,
  Download,
} from 'lucide-react';

export default function AnalyticsPage() {
  // モックデータ（実際の実装ではAPIから取得）
  const analytics = {
    overview: {
      totalViews: 15678,
      totalLikes: 892,
      totalSubscribers: 1234,
      totalRevenue: 24560,
      viewsChange: 12.5,
      likesChange: 8.3,
      subscribersChange: 15.2,
      revenueChange: 22.1,
    },
    topArticles: [
      {
        id: 1,
        title: 'TypeScript 5.0の新機能とベストプラクティス',
        views: 2345,
        likes: 156,
        publishedAt: '2024-09-08',
      },
      {
        id: 2,
        title: 'Next.js 14 App Router完全ガイド',
        views: 1890,
        likes: 134,
        publishedAt: '2024-09-07',
      },
      {
        id: 3,
        title: 'React Server Componentsの実践的活用法',
        views: 1654,
        likes: 98,
        publishedAt: '2024-09-06',
      },
    ],
    newsletterStats: {
      totalSent: 12,
      averageOpenRate: 68.5,
      averageClickRate: 12.3,
      totalSubscribers: 1234,
      newSubscribers: 45,
    },
    revenueData: [
      { month: '1月', revenue: 18000 },
      { month: '2月', revenue: 19500 },
      { month: '3月', revenue: 21000 },
      { month: '4月', revenue: 22500 },
      { month: '5月', revenue: 23000 },
      { month: '6月', revenue: 24560 },
    ],
  };

  const getChangeIcon = (change: number) => {
    if (change > 0) {
      return <TrendingUp className='h-4 w-4 text-green-600' />;
    } else if (change < 0) {
      return <TrendingDown className='h-4 w-4 text-red-600' />;
    }
    return null;
  };

  const getChangeColor = (change: number) => {
    if (change > 0) {
      return 'text-green-600';
    } else if (change < 0) {
      return 'text-red-600';
    }
    return 'text-muted-foreground';
  };

  return (
    <div className='min-h-screen bg-background'>
      <Header />
      
      <main className='container py-8'>
        <div className='mb-8'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>分析レポート</h1>
              <p className='text-muted-foreground mt-2'>
                コンテンツのパフォーマンスと収益を分析できます
              </p>
            </div>
            <Button>
              <Download className='mr-2 h-4 w-4' />
              レポートをダウンロード
            </Button>
          </div>
        </div>

        {/* 概要統計 */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    総閲覧数
                  </p>
                  <p className='text-2xl font-bold'>
                    {analytics.overview.totalViews.toLocaleString()}
                  </p>
                  <div className='flex items-center gap-1 mt-1'>
                    {getChangeIcon(analytics.overview.viewsChange)}
                    <span
                      className={`text-sm ${getChangeColor(
                        analytics.overview.viewsChange
                      )}`}
                    >
                      {analytics.overview.viewsChange > 0 ? '+' : ''}
                      {analytics.overview.viewsChange}%
                    </span>
                  </div>
                </div>
                <Eye className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    総いいね数
                  </p>
                  <p className='text-2xl font-bold'>
                    {analytics.overview.totalLikes.toLocaleString()}
                  </p>
                  <div className='flex items-center gap-1 mt-1'>
                    {getChangeIcon(analytics.overview.likesChange)}
                    <span
                      className={`text-sm ${getChangeColor(
                        analytics.overview.likesChange
                      )}`}
                    >
                      {analytics.overview.likesChange > 0 ? '+' : ''}
                      {analytics.overview.likesChange}%
                    </span>
                  </div>
                </div>
                <Star className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    購読者数
                  </p>
                  <p className='text-2xl font-bold'>
                    {analytics.overview.totalSubscribers.toLocaleString()}
                  </p>
                  <div className='flex items-center gap-1 mt-1'>
                    {getChangeIcon(analytics.overview.subscribersChange)}
                    <span
                      className={`text-sm ${getChangeColor(
                        analytics.overview.subscribersChange
                      )}`}
                    >
                      {analytics.overview.subscribersChange > 0 ? '+' : ''}
                      {analytics.overview.subscribersChange}%
                    </span>
                  </div>
                </div>
                <Users className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    総収益
                  </p>
                  <p className='text-2xl font-bold'>
                    ¥{analytics.overview.totalRevenue.toLocaleString()}
                  </p>
                  <div className='flex items-center gap-1 mt-1'>
                    {getChangeIcon(analytics.overview.revenueChange)}
                    <span
                      className={`text-sm ${getChangeColor(
                        analytics.overview.revenueChange
                      )}`}
                    >
                      {analytics.overview.revenueChange > 0 ? '+' : ''}
                      {analytics.overview.revenueChange}%
                    </span>
                  </div>
                </div>
                <BarChart3 className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* 人気記事 */}
          <Card>
            <CardHeader>
              <CardTitle>人気記事トップ3</CardTitle>
              <CardDescription>
                閲覧数とエンゲージメントの高い記事
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                {analytics.topArticles.map((article, index) => (
                  <div
                    key={article.id}
                    className='flex items-center justify-between p-4 border rounded-lg'
                  >
                    <div className='flex items-center gap-4'>
                      <div className='flex items-center justify-center w-8 h-8 bg-primary text-primary-foreground rounded-full text-sm font-bold'>
                        {index + 1}
                      </div>
                      <div>
                        <p className='font-medium'>{article.title}</p>
                        <p className='text-sm text-muted-foreground'>
                          {article.publishedAt}
                        </p>
                      </div>
                    </div>
                    <div className='text-right'>
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
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* ニュースレター統計 */}
          <Card>
            <CardHeader>
              <CardTitle>ニュースレター統計</CardTitle>
              <CardDescription>
                配信パフォーマンスの詳細
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-6'>
                <div className='grid grid-cols-2 gap-4'>
                  <div className='text-center p-4 border rounded-lg'>
                    <p className='text-2xl font-bold'>
                      {analytics.newsletterStats.totalSent}
                    </p>
                    <p className='text-sm text-muted-foreground'>総配信数</p>
                  </div>
                  <div className='text-center p-4 border rounded-lg'>
                    <p className='text-2xl font-bold'>
                      {analytics.newsletterStats.totalSubscribers}
                    </p>
                    <p className='text-sm text-muted-foreground'>購読者数</p>
                  </div>
                </div>
                
                <div className='space-y-4'>
                  <div className='flex items-center justify-between'>
                    <span className='text-sm font-medium'>平均開封率</span>
                    <div className='flex items-center gap-2'>
                      <div className='w-32 bg-muted rounded-full h-2'>
                        <div
                          className='bg-primary h-2 rounded-full'
                          style={{
                            width: `${analytics.newsletterStats.averageOpenRate}%`,
                          }}
                        ></div>
                      </div>
                      <span className='text-sm font-medium'>
                        {analytics.newsletterStats.averageOpenRate}%
                      </span>
                    </div>
                  </div>
                  
                  <div className='flex items-center justify-between'>
                    <span className='text-sm font-medium'>平均クリック率</span>
                    <div className='flex items-center gap-2'>
                      <div className='w-32 bg-muted rounded-full h-2'>
                        <div
                          className='bg-green-500 h-2 rounded-full'
                          style={{
                            width: `${analytics.newsletterStats.averageClickRate}%`,
                          }}
                        ></div>
                      </div>
                      <span className='text-sm font-medium'>
                        {analytics.newsletterStats.averageClickRate}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className='pt-4 border-t'>
                  <div className='flex items-center justify-between'>
                    <span className='text-sm font-medium'>今月の新規購読者</span>
                    <Badge className='bg-green-100 text-green-800'>
                      +{analytics.newsletterStats.newSubscribers}
                    </Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 収益グラフ */}
        <Card className='mt-8'>
          <CardHeader>
            <CardTitle>月別収益推移</CardTitle>
            <CardDescription>
              過去6ヶ月の収益パフォーマンス
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className='h-64 flex items-end justify-between gap-2'>
              {analytics.revenueData.map((data, index) => (
                <div key={data.month} className='flex flex-col items-center gap-2'>
                  <div
                    className='bg-primary rounded-t w-12'
                    style={{
                      height: `${(data.revenue / 25000) * 200}px`,
                    }}
                  ></div>
                  <div className='text-xs text-muted-foreground'>
                    {data.month}
                  </div>
                  <div className='text-xs font-medium'>
                    ¥{data.revenue.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>

      <Footer />
    </div>
  );
}
