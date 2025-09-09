'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Check, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { createCheckoutSession } from '@/lib/stripe';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function PricingPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);

  const plans = [
    {
      id: 'free',
      name: 'フリー',
      price: '¥0',
      period: '月',
      description: '基本的な機能をお試しください',
      features: [
        '週1回のトレンドレポート',
        '基本記事の閲覧',
        'コミュニティアクセス',
        'メールサポート',
      ],
      cta: '無料で始める',
      popular: false,
      priceId: null,
    },
    {
      id: 'premium',
      name: 'プレミアム',
      price: '¥1,980',
      period: '月',
      description: '本格的なTypeScript開発者向け',
      features: [
        '日次トレンドレポート',
        '全記事の閲覧',
        'プレミアムコンテンツ',
        '優先サポート',
        'API アクセス',
        'カスタム分析',
      ],
      cta: 'プレミアムを開始',
      popular: true,
      priceId: 'price_premium_monthly', // Stripe Price ID
    },
    {
      id: 'enterprise',
      name: 'エンタープライズ',
      price: 'カスタム',
      period: '',
      description: 'チーム・企業向けソリューション',
      features: [
        '無制限アクセス',
        'チーム管理機能',
        'カスタムブランディング',
        '専任サポート',
        'オンプレミス対応',
        'SLA保証',
      ],
      cta: 'お問い合わせ',
      popular: false,
      priceId: null,
    },
  ];

  const handleSubscribe = async (plan: typeof plans[0]) => {
    if (!session) {
      router.push('/auth/signin');
      return;
    }

    if (plan.id === 'free') {
      // フリープランの場合は直接ダッシュボードへ
      router.push('/dashboard');
      return;
    }

    if (plan.id === 'enterprise') {
      // エンタープライズプランの場合はお問い合わせページへ
      router.push('/contact');
      return;
    }

    if (!plan.priceId) {
      return;
    }

    setLoading(plan.id);
    try {
      const sessionId = await createCheckoutSession(plan.priceId);
      
      const stripe = (await import('@stripe/stripe-js')).loadStripe(
        process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
      );
      
      const stripeInstance = await stripe;
      if (stripeInstance) {
        await stripeInstance.redirectToCheckout({ sessionId });
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <Header />
      
      <main className='container py-20'>
        <div className='mx-auto max-w-2xl text-center mb-16'>
          <h1 className='text-4xl font-bold tracking-tight sm:text-6xl mb-6'>
            料金プラン
          </h1>
          <p className='text-lg text-muted-foreground sm:text-xl'>
            あなたのニーズに合わせたプランを選択してください
          </p>
        </div>
        
        <div className='grid grid-cols-1 gap-8 lg:grid-cols-3'>
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative ${
                plan.popular
                  ? 'border-primary bg-primary/5'
                  : 'border-border'
              }`}
            >
              {plan.popular && (
                <div className='absolute -top-4 left-1/2 -translate-x-1/2'>
                  <span className='rounded-full bg-primary px-4 py-1 text-sm font-medium text-primary-foreground'>
                    人気
                  </span>
                </div>
              )}
              
              <CardHeader className='text-center'>
                <CardTitle className='text-xl font-semibold'>{plan.name}</CardTitle>
                <CardDescription className='mt-2 text-sm text-muted-foreground'>
                  {plan.description}
                </CardDescription>
                <div className='mt-4'>
                  <span className='text-4xl font-bold'>{plan.price}</span>
                  {plan.period && (
                    <span className='text-muted-foreground'>/{plan.period}</span>
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                <ul className='space-y-4'>
                  {plan.features.map((feature) => (
                    <li key={feature} className='flex items-start'>
                      <Check className='mr-3 h-5 w-5 flex-shrink-0 text-primary' />
                      <span className='text-sm'>{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <div className='mt-8'>
                  <Button
                    className='w-full'
                    variant={plan.popular ? 'default' : 'outline'}
                    onClick={() => handleSubscribe(plan)}
                    disabled={loading === plan.id}
                  >
                    {loading === plan.id ? (
                      <>
                        <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                        処理中...
                      </>
                    ) : (
                      plan.cta
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className='mt-16 text-center'>
          <p className='text-sm text-muted-foreground'>
            すべてのプランには14日間の無料トライアルが含まれます
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}
