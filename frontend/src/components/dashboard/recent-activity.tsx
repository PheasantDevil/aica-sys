'use client';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Activity, BookOpen, Mail, TrendingUp } from 'lucide-react';

export function RecentActivity() {
  // Mock data - in production this would come from an API
  const activities = [
    {
      id: '1',
      type: 'article_read',
      title: 'TypeScript 5.0の新機能について',
      description: '記事を読みました',
      timestamp: '2時間前',
      icon: BookOpen,
      color: 'blue',
    },
    {
      id: '2',
      type: 'newsletter_received',
      title: '週刊TypeScriptニュース #42',
      description: 'ニュースレターを受信しました',
      timestamp: '1日前',
      icon: Mail,
      color: 'green',
    },
    {
      id: '3',
      type: 'trend_viewed',
      title: 'Next.js 14の採用率上昇',
      description: 'トレンド分析を確認しました',
      timestamp: '2日前',
      icon: TrendingUp,
      color: 'purple',
    },
    {
      id: '4',
      type: 'subscription_created',
      title: 'プレミアムプランに加入',
      description: 'サブスクリプションを開始しました',
      timestamp: '3日前',
      icon: Activity,
      color: 'orange',
    },
  ];

  const getActivityIcon = (type: string) => {
    const activity = activities.find(a => a.id === '1'); // Default to first activity
    return activity?.icon || Activity;
  };

  const getActivityColor = (type: string) => {
    const colorMap: Record<string, string> = {
      article_read: 'text-blue-600 bg-blue-100',
      newsletter_received: 'text-green-600 bg-green-100',
      trend_viewed: 'text-purple-600 bg-purple-100',
      subscription_created: 'text-orange-600 bg-orange-100',
    };
    return colorMap[type] || 'text-gray-600 bg-gray-100';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className='flex items-center gap-2'>
          <Activity className='h-5 w-5' />
          最近のアクティビティ
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className='space-y-4'>
          {activities.map(activity => {
            const Icon = activity.icon;
            return (
              <div key={activity.id} className='flex items-start gap-3'>
                <div
                  className={`p-2 rounded-full ${getActivityColor(
                    activity.type
                  )}`}
                >
                  <Icon className='h-4 w-4' />
                </div>
                <div className='flex-1 min-w-0'>
                  <div className='flex items-center justify-between'>
                    <p className='text-sm font-medium text-gray-900 truncate'>
                      {activity.title}
                    </p>
                    <Badge variant='outline' className='text-xs'>
                      {activity.timestamp}
                    </Badge>
                  </div>
                  <p className='text-sm text-gray-500 mt-1'>
                    {activity.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        <div className='mt-4 pt-4 border-t'>
          <a
            href='/dashboard/activity'
            className='text-sm text-blue-600 hover:text-blue-800 font-medium'
          >
            すべてのアクティビティを見る →
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
