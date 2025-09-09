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
import {
  Calendar,
  DollarSign,
  FileText,
  Mail,
  Star,
  TrendingUp,
  Users,
} from 'lucide-react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/signin');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className='min-h-screen flex items-center justify-center'>
        <div className='animate-spin rounded-full h-32 w-32 border-b-2 border-primary'></div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const stats = [
    {
      title: '総収益',
      value: '¥12,450',
      change: '+12.5%',
      icon: DollarSign,
      color: 'text-green-600',
    },
    {
      title: '購読者数',
      value: '1,234',
      change: '+8.2%',
      icon: Users,
      color: 'text-blue-600',
    },
    {
      title: '記事数',
      value: '45',
      change: '+3.2%',
      icon: FileText,
      color: 'text-purple-600',
    },
    {
      title: 'ニュースレター',
      value: '12',
      change: '+15.3%',
      icon: Mail,
      color: 'text-orange-600',
    },
  ];

  const recentArticles = [
    {
      id: 1,
      title: 'TypeScript 5.0の新機能とベストプラクティス',
      views: 1234,
      likes: 89,
      publishedAt: '2024-09-08',
    },
    {
      id: 2,
      title: 'Next.js 14 App Router完全ガイド',
      views: 987,
      likes: 67,
      publishedAt: '2024-09-07',
    },
    {
      id: 3,
      title: 'React Server Componentsの実践的活用法',
      views: 756,
      likes: 45,
      publishedAt: '2024-09-06',
    },
  ];

  return (
    <div className='min-h-screen bg-background'>
      <Header />

      <main className='container py-8'>
        <div className='mb-8'>
          <h1 className='text-3xl font-bold text-foreground'>ダッシュボード</h1>
          <p className='text-muted-foreground mt-2'>
            おかえりなさい、{session.user?.name || session.user?.email}さん
          </p>
        </div>

        {/* 統計カード */}
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8'>
          {stats.map(stat => (
            <Card key={stat.title}>
              <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
                <CardTitle className='text-sm font-medium'>
                  {stat.title}
                </CardTitle>
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className='text-2xl font-bold'>{stat.value}</div>
                <p className={`text-xs ${stat.color}`}>{stat.change} 先月比</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* 最近の記事 */}
          <Card>
            <CardHeader>
              <CardTitle>最近の記事</CardTitle>
              <CardDescription>最新のパフォーマンス状況</CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                {recentArticles.map(article => (
                  <div
                    key={article.id}
                    className='flex items-center justify-between'
                  >
                    <div className='space-y-1'>
                      <p className='text-sm font-medium leading-none'>
                        {article.title}
                      </p>
                      <p className='text-xs text-muted-foreground'>
                        {article.publishedAt}
                      </p>
                    </div>
                    <div className='flex items-center space-x-4 text-xs text-muted-foreground'>
                      <div className='flex items-center space-x-1'>
                        <TrendingUp className='h-3 w-3' />
                        <span>{article.views}</span>
                      </div>
                      <div className='flex items-center space-x-1'>
                        <Star className='h-3 w-3' />
                        <span>{article.likes}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <Button variant='outline' className='w-full mt-4'>
                すべての記事を見る
              </Button>
            </CardContent>
          </Card>

          {/* 今週のスケジュール */}
          <Card>
            <CardHeader>
              <CardTitle>今週のスケジュール</CardTitle>
              <CardDescription>自動生成・公開予定</CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-4'>
                <div className='flex items-center space-x-4'>
                  <Calendar className='h-4 w-4 text-primary' />
                  <div>
                    <p className='text-sm font-medium'>月曜日 9:00</p>
                    <p className='text-xs text-muted-foreground'>
                      TypeScript週間レポート自動生成
                    </p>
                  </div>
                </div>
                <div className='flex items-center space-x-4'>
                  <Calendar className='h-4 w-4 text-primary' />
                  <div>
                    <p className='text-sm font-medium'>水曜日 14:00</p>
                    <p className='text-xs text-muted-foreground'>
                      技術記事自動公開
                    </p>
                  </div>
                </div>
                <div className='flex items-center space-x-4'>
                  <Calendar className='h-4 w-4 text-primary' />
                  <div>
                    <p className='text-sm font-medium'>金曜日 10:00</p>
                    <p className='text-xs text-muted-foreground'>
                      ニュースレター配信
                    </p>
                  </div>
                </div>
              </div>
              <Button variant='outline' className='w-full mt-4'>
                スケジュールを管理
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
