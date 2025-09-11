'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useSubscription } from '@/hooks/use-subscription';
import { Crown, Calendar, CreditCard } from 'lucide-react';
import Link from 'next/link';

export function SubscriptionStatus() {
  const { subscription, isLoading } = useSubscription();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>サブスクリプション状況</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-20 animate-pulse bg-muted rounded"></div>
        </CardContent>
      </Card>
    );
  }

  const getPlanInfo = (plan: string) => {
    switch (plan) {
      case 'premium':
        return {
          name: 'プレミアム',
          color: 'bg-primary',
          icon: Crown,
        };
      case 'enterprise':
        return {
          name: 'エンタープライズ',
          color: 'bg-purple-500',
          icon: Crown,
        };
      default:
        return {
          name: 'フリー',
          color: 'bg-muted',
          icon: CreditCard,
        };
    }
  };

  const planInfo = getPlanInfo(subscription?.plan || 'free');
  const Icon = planInfo.icon;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className="h-5 w-5" />
          サブスクリプション状況
        </CardTitle>
        <CardDescription>
          現在のプランと利用状況
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Badge className={`${planInfo.color} text-white`}>
              {planInfo.name}
            </Badge>
            {subscription?.status === 'active' && (
              <Badge variant="outline" className="text-green-600 border-green-600">
                アクティブ
              </Badge>
            )}
          </div>
          
          {subscription?.plan === 'free' && (
            <Button asChild>
              <Link href="/pricing">
                アップグレード
              </Link>
            </Button>
          )}
        </div>

        {subscription?.stripeCurrentPeriodEnd && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>
              次回更新日: {new Date(subscription.stripeCurrentPeriodEnd).toLocaleDateString('ja-JP')}
            </span>
          </div>
        )}

        {subscription?.plan === 'free' && (
          <div className="p-4 bg-muted/50 rounded-lg">
            <p className="text-sm text-muted-foreground">
              プレミアムプランにアップグレードして、より多くの機能をご利用ください。
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
