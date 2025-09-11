'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { FileText, Mail, TrendingUp, ExternalLink } from 'lucide-react';
import Link from 'next/link';

export function RecentContent() {
  // モックデータ - 実際の実装ではAPIから取得
  const recentContent = [
    {
      id: '1',
      type: 'article',
      title: 'TypeScript 5.0の新機能とベストプラクティス',
      description: '最新のTypeScript 5.0で追加された新機能について詳しく解説します。',
      publishedAt: '2024-01-15',
      views: 1234,
      likes: 89,
      icon: FileText,
      href: '/articles/typescript-5-0-features',
    },
    {
      id: '2',
      type: 'newsletter',
      title: '週刊TypeScriptニュース #42',
      description: '今週のTypeScriptエコシステムの重要なアップデートをお届けします。',
      publishedAt: '2024-01-14',
      subscribers: 2341,
      openRate: 78,
      icon: Mail,
      href: '/newsletters/weekly-42',
    },
    {
      id: '3',
      type: 'trend',
      title: '2024年TypeScriptトレンド分析',
      description: '2024年のTypeScriptエコシステムの主要トレンドを分析しました。',
      publishedAt: '2024-01-13',
      engagement: 92,
      shares: 156,
      icon: TrendingUp,
      href: '/trends/2024-analysis',
    },
  ];

  const getTypeInfo = (type: string) => {
    switch (type) {
      case 'article':
        return { label: '記事', color: 'bg-blue-500' };
      case 'newsletter':
        return { label: 'ニュースレター', color: 'bg-green-500' };
      case 'trend':
        return { label: 'トレンド', color: 'bg-purple-500' };
      default:
        return { label: 'コンテンツ', color: 'bg-gray-500' };
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>最近のコンテンツ</CardTitle>
        <CardDescription>
          最近作成・公開されたコンテンツ
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentContent.map((content) => {
            const typeInfo = getTypeInfo(content.type);
            const Icon = content.icon;
            
            return (
              <div
                key={content.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-muted">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className={`${typeInfo.color} text-white text-xs`}>
                        {typeInfo.label}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(content.publishedAt).toLocaleDateString('ja-JP')}
                      </span>
                    </div>
                    <h3 className="font-medium text-sm mb-1">{content.title}</h3>
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {content.description}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      {content.views && <span>閲覧: {content.views}</span>}
                      {content.likes && <span>いいね: {content.likes}</span>}
                      {content.subscribers && <span>購読者: {content.subscribers}</span>}
                      {content.engagement && <span>エンゲージメント: {content.engagement}%</span>}
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm" asChild>
                  <Link href={content.href}>
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 pt-4 border-t">
          <Button variant="outline" className="w-full" asChild>
            <Link href="/content">
              すべてのコンテンツを見る
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
