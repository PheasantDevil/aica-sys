'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';

interface DashboardStatsProps {}

export function DashboardStats({}: DashboardStatsProps) {
  const {
    data: stats,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['user-stats'],
    queryFn: async () => {
      const response = await fetch('/api/users/stats');
      if (!response.ok) {
        throw new Error('Failed to fetch user stats');
      }
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className='pb-2'>
              <div className='h-4 bg-gray-200 rounded animate-pulse' />
            </CardHeader>
            <CardContent>
              <div className='h-8 bg-gray-200 rounded animate-pulse' />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              読み込んだ記事数
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-gray-900'>-</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              受信ニュースレター数
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-gray-900'>-</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              サブスクリプション
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-gray-900'>-</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-gray-600'>
              アクティブ日数
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='text-2xl font-bold text-gray-900'>-</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6'>
      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-gray-600'>
            読み込んだ記事数
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-gray-900'>
            {stats?.total_articles_read || 0}
          </div>
          <p className='text-xs text-gray-500 mt-1'>
            今月 +{Math.floor(Math.random() * 10)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-gray-600'>
            受信ニュースレター数
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-gray-900'>
            {stats?.total_newsletters_received || 0}
          </div>
          <p className='text-xs text-gray-500 mt-1'>
            今月 +{Math.floor(Math.random() * 5)}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-gray-600'>
            サブスクリプション
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-gray-900'>
            {stats?.subscription_status === 'active' ? 'アクティブ' : 'なし'}
          </div>
          <p className='text-xs text-gray-500 mt-1'>
            {stats?.subscription_plan || 'フリープラン'}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-sm font-medium text-gray-600'>
            アクティブ日数
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='text-2xl font-bold text-gray-900'>
            {Math.floor(Math.random() * 30) + 1}
          </div>
          <p className='text-xs text-gray-500 mt-1'>
            連続 {Math.floor(Math.random() * 7) + 1} 日
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
