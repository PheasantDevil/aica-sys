'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  BookOpen,
  CreditCard,
  Mail,
  Settings,
  TrendingUp,
  User,
} from 'lucide-react';

export function QuickActions() {
  const actions = [
    {
      title: '記事を読む',
      description: '最新のTypeScript記事をチェック',
      icon: BookOpen,
      href: '/articles',
      color: 'bg-blue-500 hover:bg-blue-600',
    },
    {
      title: 'ニュースレター',
      description: '購読状況を確認',
      icon: Mail,
      href: '/newsletters',
      color: 'bg-green-500 hover:bg-green-600',
    },
    {
      title: 'トレンド分析',
      description: '最新のトレンドを確認',
      icon: TrendingUp,
      href: '/trends',
      color: 'bg-purple-500 hover:bg-purple-600',
    },
    {
      title: 'プロフィール',
      description: 'アカウント設定を更新',
      icon: User,
      href: '/dashboard/profile',
      color: 'bg-gray-500 hover:bg-gray-600',
    },
    {
      title: 'サブスクリプション',
      description: 'プランを管理',
      icon: CreditCard,
      href: '/dashboard/subscription',
      color: 'bg-orange-500 hover:bg-orange-600',
    },
    {
      title: '設定',
      description: 'アプリケーション設定',
      icon: Settings,
      href: '/dashboard/settings',
      color: 'bg-indigo-500 hover:bg-indigo-600',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>クイックアクション</CardTitle>
      </CardHeader>
      <CardContent>
        <div className='grid grid-cols-1 gap-3'>
          {actions.map(action => {
            const Icon = action.icon;
            return (
              <Button
                key={action.title}
                variant='outline'
                className='justify-start h-auto p-4'
                asChild
              >
                <a href={action.href}>
                  <div className='flex items-center gap-3'>
                    <div
                      className={`p-2 rounded-md text-white ${action.color}`}
                    >
                      <Icon className='h-4 w-4' />
                    </div>
                    <div className='text-left'>
                      <div className='font-medium'>{action.title}</div>
                      <div className='text-sm text-gray-500'>
                        {action.description}
                      </div>
                    </div>
                  </div>
                </a>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
