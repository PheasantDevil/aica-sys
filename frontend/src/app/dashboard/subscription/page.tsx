'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Badge } from '@/components/ui/badge';
import { 
  CheckCircle, 
  XCircle, 
  Calendar, 
  CreditCard, 
  Settings,
  ExternalLink
} from 'lucide-react';
import { useState } from 'react';
import { createPortalSession } from '@/lib/stripe';
import { useSession } from 'next-auth/react';

export default function SubscriptionPage() {
  const { data: session } = useSession();
  const [loading, setLoading] = useState(false);

  // モックデータ（実際の実装ではAPIから取得）
  const subscription = {
    id: 'sub_1234567890',
    status: 'active',
    plan: 'premium',
    planName: 'プレミアム',
    price: '¥1,980',
    period: '月',
    currentPeriodStart: '2024-09-01',
    currentPeriodEnd: '2024-10-01',
    cancelAtPeriodEnd: false,
    nextBillingDate: '2024-10-01',
    paymentMethod: {
      type: 'card',
      last4: '4242',
      brand: 'visa',
    },
  };

  const handleManageSubscription = async () => {
    if (!session?.user?.email) return;

    setLoading(true);
    try {
      // 実際の実装では、ユーザーのStripe Customer IDを取得
      const customerId = 'cus_mock_customer_id';
      const url = await createPortalSession(customerId);
      window.open(url, '_blank');
    } catch (error) {
      console.error('Error opening customer portal:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className='bg-green-100 text-green-800'><CheckCircle className='w-3 h-3 mr-1' />アクティブ</Badge>;
      case 'canceled':
        return <Badge variant='destructive'><XCircle className='w-3 h-3 mr-1' />キャンセル済み</Badge>;
      case 'past_due':
        return <Badge variant='destructive'><XCircle className='w-3 h-3 mr-1' />支払い遅延</Badge>;
      default:
        return <Badge variant='secondary'>{status}</Badge>;
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <Header />
      
      <main className='container py-8'>
        <div className='mb-8'>
          <h1 className='text-3xl font-bold text-foreground'>サブスクリプション管理</h1>
          <p className='text-muted-foreground mt-2'>
            現在のプランと支払い情報を管理できます
          </p>
        </div>

        <div className='grid grid-cols-1 lg:grid-cols-2 gap-8'>
          {/* 現在のプラン */}
          <Card>
            <CardHeader>
              <CardTitle className='flex items-center justify-between'>
                現在のプラン
                {getStatusBadge(subscription.status)}
              </CardTitle>
              <CardDescription>
                サブスクリプションの詳細情報
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-4'>
              <div className='flex items-center justify-between'>
                <span className='text-sm font-medium'>プラン</span>
                <span className='text-sm'>{subscription.planName}</span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-sm font-medium'>料金</span>
                <span className='text-sm'>{subscription.price}/{subscription.period}</span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-sm font-medium'>次の請求日</span>
                <span className='text-sm'>{subscription.nextBillingDate}</span>
              </div>
              <div className='flex items-center justify-between'>
                <span className='text-sm font-medium'>支払い方法</span>
                <span className='text-sm capitalize'>
                  {subscription.paymentMethod.brand} •••• {subscription.paymentMethod.last4}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* 支払い履歴 */}
          <Card>
            <CardHeader>
              <CardTitle>支払い履歴</CardTitle>
              <CardDescription>
                最近の支払い記録
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className='space-y-3'>
                <div className='flex items-center justify-between py-2 border-b'>
                  <div className='flex items-center space-x-3'>
                    <CheckCircle className='h-4 w-4 text-green-600' />
                    <div>
                      <p className='text-sm font-medium'>プレミアムプラン</p>
                      <p className='text-xs text-muted-foreground'>2024-09-01</p>
                    </div>
                  </div>
                  <span className='text-sm font-medium'>¥1,980</span>
                </div>
                <div className='flex items-center justify-between py-2 border-b'>
                  <div className='flex items-center space-x-3'>
                    <CheckCircle className='h-4 w-4 text-green-600' />
                    <div>
                      <p className='text-sm font-medium'>プレミアムプラン</p>
                      <p className='text-xs text-muted-foreground'>2024-08-01</p>
                    </div>
                  </div>
                  <span className='text-sm font-medium'>¥1,980</span>
                </div>
                <div className='flex items-center justify-between py-2'>
                  <div className='flex items-center space-x-3'>
                    <CheckCircle className='h-4 w-4 text-green-600' />
                    <div>
                      <p className='text-sm font-medium'>プレミアムプラン</p>
                      <p className='text-xs text-muted-foreground'>2024-07-01</p>
                    </div>
                  </div>
                  <span className='text-sm font-medium'>¥1,980</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 管理アクション */}
        <div className='mt-8'>
          <Card>
            <CardHeader>
              <CardTitle>サブスクリプション管理</CardTitle>
              <CardDescription>
                支払い方法の変更、プランの変更、キャンセルなどができます
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className='flex flex-col sm:flex-row gap-4'>
                <Button
                  onClick={handleManageSubscription}
                  disabled={loading}
                  className='flex items-center'
                >
                  <Settings className='mr-2 h-4 w-4' />
                  {loading ? '処理中...' : 'Stripe カスタマーポータルで管理'}
                  <ExternalLink className='ml-2 h-4 w-4' />
                </Button>
                <Button variant='outline' disabled>
                  <CreditCard className='mr-2 h-4 w-4' />
                  支払い方法を変更
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
