'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Users, FileText, BarChart3 } from 'lucide-react';

export function DashboardOverview() {
  // モックデータ - 実際の実装ではAPIから取得
  const stats = [
    {
      title: '今月の記事閲覧数',
      value: '1,234',
      change: '+12%',
      changeType: 'positive' as const,
      icon: FileText,
    },
    {
      title: 'アクティブユーザー',
      value: '456',
      change: '+8%',
      changeType: 'positive' as const,
      icon: Users,
    },
    {
      title: '生成されたコンテンツ',
      value: '89',
      change: '+23%',
      changeType: 'positive' as const,
      icon: TrendingUp,
    },
    {
      title: 'エンゲージメント率',
      value: '78%',
      change: '+5%',
      changeType: 'positive' as const,
      icon: BarChart3,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                <span className={`${
                  stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.change}
                </span>
                {' '}先月比
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
