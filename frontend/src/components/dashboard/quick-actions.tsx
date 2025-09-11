'use client';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  BarChart3,
  CreditCard,
  FileText,
  HelpCircle,
  Mail,
  Settings,
  TrendingUp,
} from 'lucide-react';
import Link from 'next/link';

export function QuickActions() {
  const actions = [
    {
      title: '新しい記事を作成',
      description: 'AIを使って新しい記事を生成',
      icon: FileText,
      href: '/content/articles/new',
      color: 'bg-blue-500',
    },
    {
      title: 'ニュースレター配信',
      description: '購読者にニュースレターを送信',
      icon: Mail,
      href: '/content/newsletters/new',
      color: 'bg-green-500',
    },
    {
      title: 'トレンド分析',
      description: '最新のトレンドを分析',
      icon: TrendingUp,
      href: '/trends/analyze',
      color: 'bg-purple-500',
    },
    {
      title: 'アナリティクス',
      description: '詳細な分析データを確認',
      icon: BarChart3,
      href: '/analytics',
      color: 'bg-orange-500',
    },
    {
      title: 'サブスクリプション管理',
      description: 'プラン変更や支払い設定',
      icon: CreditCard,
      href: '/settings/subscription',
      color: 'bg-indigo-500',
    },
    {
      title: '設定',
      description: 'アカウント設定を変更',
      icon: Settings,
      href: '/settings',
      color: 'bg-gray-500',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>クイックアクション</CardTitle>
        <CardDescription>よく使用する機能にすばやくアクセス</CardDescription>
      </CardHeader>
      <CardContent>
        <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
          {actions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Button
                key={index}
                variant='outline'
                className='h-auto p-4 flex flex-col items-start gap-2 hover:bg-muted/50'
                asChild
              >
                <Link href={action.href}>
                  <div className='flex items-center gap-3 w-full'>
                    <div
                      className={`p-2 rounded-lg ${action.color} text-white`}
                    >
                      <Icon className='h-4 w-4' />
                    </div>
                    <div className='text-left'>
                      <div className='font-medium text-sm'>{action.title}</div>
                      <div className='text-xs text-muted-foreground'>
                        {action.description}
                      </div>
                    </div>
                  </div>
                </Link>
              </Button>
            );
          })}
        </div>

        <div className='mt-6 p-4 bg-muted/50 rounded-lg'>
          <div className='flex items-center gap-2 mb-2'>
            <HelpCircle className='h-4 w-4 text-muted-foreground' />
            <span className='text-sm font-medium'>ヘルプが必要ですか？</span>
          </div>
          <p className='text-xs text-muted-foreground mb-3'>
            よくある質問やサポート情報をご確認ください。
          </p>
          <Button variant='outline' size='sm' asChild>
            <Link href='/help'>ヘルプセンター</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
