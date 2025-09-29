'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { Calendar, CreditCard, Settings } from 'lucide-react';

export function SubscriptionStatus() {
  const { data: subscription, isLoading, error } = useQuery({
    queryKey: ['user-subscription'],
    queryFn: async () => {
      const response = await fetch('/api/users/subscription');
      if (!response.ok) {
        throw new Error('Failed to fetch subscription');
      }
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            サブスクリプション状況
          </CardTitle>
        </CardHeader>
        <CardContent>
          <LoadingSpinner />
        </CardContent>
      </Card>
    );
  }

  if (error || !subscription?.subscription) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            サブスクリプション状況
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-500 mb-4">
              現在サブスクリプションはありません
            </div>
            <div className="space-y-2">
              <Button asChild className="w-full">
                <a href="/pricing">プランを選択</a>
              </Button>
              <Button variant="outline" asChild className="w-full">
                <a href="/pricing">詳細を見る</a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const sub = subscription.subscription;
  const isActive = sub.status === 'active';
  const isCanceled = sub.cancel_at_period_end;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          サブスクリプション状況
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">ステータス:</span>
              <Badge variant={isActive ? 'default' : 'secondary'}>
                {isActive ? 'アクティブ' : sub.status}
              </Badge>
            </div>
            {isCanceled && (
              <Badge variant="destructive">期間終了時にキャンセル</Badge>
            )}
          </div>

          {/* Plan Info */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">プラン:</span>
              <span className="text-sm">{sub.plan?.name || 'Unknown'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">料金:</span>
              <span className="text-sm">
                ¥{sub.plan?.price?.toLocaleString() || '0'}/月
              </span>
            </div>
          </div>

          {/* Next Billing */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Calendar className="h-4 w-4" />
            <span>
              次回請求日: {new Date(sub.current_period_end).toLocaleDateString('ja-JP')}
            </span>
          </div>

          {/* Features */}
          {sub.plan?.features && (
            <div className="space-y-2">
              <span className="text-sm font-medium">含まれる機能:</span>
              <div className="flex flex-wrap gap-1">
                {sub.plan.features.map((feature: string, index: number) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {feature.replace(/_/g, ' ')}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-4">
            <Button variant="outline" size="sm" asChild>
              <a href="/dashboard/subscription">
                <Settings className="h-4 w-4 mr-2" />
                管理
              </a>
            </Button>
            {isActive && !isCanceled && (
              <Button variant="outline" size="sm" asChild>
                <a href="/dashboard/subscription/cancel">キャンセル</a>
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}