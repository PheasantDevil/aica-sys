'use client';

import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { CheckoutForm } from '@/components/payment/checkout-form';
import { OrderSummary } from '@/components/payment/order-summary';
import { useSubscription } from '@/hooks/use-subscription';
import { useSession } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';

export default function CheckoutPage() {
  const { data: session } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { subscription } = useSubscription();
  const [isLoading, setIsLoading] = useState(true);

  const priceId = searchParams.get('priceId');
  const plan = searchParams.get('plan') || 'premium';

  useEffect(() => {
    if (!session) {
      router.push('/auth/signin?callbackUrl=/checkout');
      return;
    }

    if (subscription?.isPaid) {
      router.push('/dashboard');
      return;
    }

    setIsLoading(false);
  }, [session, subscription, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container py-20">
          <div className="flex items-center justify-center">
            <div className="flex items-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>読み込み中...</span>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">お支払い</h1>
            <p className="text-muted-foreground">
              プレミアムプランにアップグレードして、すべての機能をご利用ください
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="order-2 lg:order-1">
              <CheckoutForm priceId={priceId} plan={plan} />
            </div>
            
            <div className="order-1 lg:order-2">
              <OrderSummary plan={plan} />
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
