import { DashboardHeader } from '@/components/dashboard/dashboard-header';
import { DashboardStats } from '@/components/dashboard/dashboard-stats';
import { QuickActions } from '@/components/dashboard/quick-actions';
import { RecentActivity } from '@/components/dashboard/recent-activity';
import { SubscriptionStatus } from '@/components/dashboard/subscription-status';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { authOptions } from '@/lib/auth';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { Suspense } from 'react';

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    redirect('/auth/signin');
  }

  return (
    <div className='min-h-screen bg-gray-50'>
      <DashboardHeader user={session.user} />

      <main className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'>
        <div className='space-y-8'>
          {/* Welcome Section */}
          <div className='bg-white rounded-lg shadow p-6'>
            <h1 className='text-2xl font-bold text-gray-900 mb-2'>
              Welcome back, {session.user.name || session.user.email}!
            </h1>
            <p className='text-gray-600'>
              Here's what's happening with your AICA-SyS account.
            </p>
          </div>

          {/* Stats Grid */}
          <Suspense fallback={<LoadingSpinner />}>
            <DashboardStats />
          </Suspense>

          {/* Main Content Grid */}
          <div className='grid grid-cols-1 lg:grid-cols-3 gap-8'>
            {/* Left Column */}
            <div className='lg:col-span-2 space-y-8'>
              {/* Subscription Status */}
              <Suspense fallback={<LoadingSpinner />}>
                <SubscriptionStatus />
              </Suspense>

              {/* Recent Activity */}
              <Suspense fallback={<LoadingSpinner />}>
                <RecentActivity />
              </Suspense>
            </div>

            {/* Right Column */}
            <div className='space-y-8'>
              {/* Quick Actions */}
              <QuickActions />

              {/* Recent Articles */}
              <Suspense fallback={<LoadingSpinner />}>
                <RecentArticles />
              </Suspense>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function RecentArticles() {
  // This would fetch recent articles from the API
  const articles = [
    {
      id: '1',
      title: 'TypeScript 5.0の新機能',
      excerpt: 'TypeScript 5.0で追加された新機能について詳しく解説します。',
      publishedAt: '2024-01-15',
      readTime: '5分',
    },
    {
      id: '2',
      title: 'Next.js 14のApp Router完全ガイド',
      excerpt: 'Next.js 14のApp Routerの使い方を完全に解説します。',
      publishedAt: '2024-01-14',
      readTime: '8分',
    },
  ];

  return (
    <div className='bg-white rounded-lg shadow p-6'>
      <h2 className='text-lg font-semibold text-gray-900 mb-4'>最新記事</h2>
      <div className='space-y-4'>
        {articles.map(article => (
          <div
            key={article.id}
            className='border-b border-gray-200 pb-4 last:border-b-0'
          >
            <h3 className='font-medium text-gray-900 mb-1'>{article.title}</h3>
            <p className='text-sm text-gray-600 mb-2'>{article.excerpt}</p>
            <div className='flex items-center text-xs text-gray-500'>
              <span>{article.publishedAt}</span>
              <span className='mx-2'>•</span>
              <span>{article.readTime}</span>
            </div>
          </div>
        ))}
      </div>
      <div className='mt-4'>
        <a
          href='/articles'
          className='text-sm text-blue-600 hover:text-blue-800 font-medium'
        >
          すべての記事を見る →
        </a>
      </div>
    </div>
  );
}
