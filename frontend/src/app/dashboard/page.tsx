'use client';

import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { DashboardOverview } from '@/components/dashboard/dashboard-overview';
import { SubscriptionStatus } from '@/components/dashboard/subscription-status';
import { RecentContent } from '@/components/dashboard/recent-content';
import { QuickActions } from '@/components/dashboard/quick-actions';

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/auth/signin');
    }
  }, [session, status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container py-20">
          <div className="flex items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            ダッシュボード
          </h1>
          <p className="text-muted-foreground">
            ようこそ、{session.user?.name || session.user?.email}さん
          </p>
        </div>

        <div className="grid gap-8">
          {/* サブスクリプション状況 */}
          <SubscriptionStatus />
          
          {/* ダッシュボード概要 */}
          <DashboardOverview />
          
          {/* 最近のコンテンツ */}
          <RecentContent />
          
          {/* クイックアクション */}
          <QuickActions />
        </div>
      </main>

      <Footer />
    </div>
  );
}