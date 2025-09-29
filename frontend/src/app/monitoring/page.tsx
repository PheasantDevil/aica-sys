import { Suspense } from 'react';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '@/lib/auth';
import { MonitoringDashboard } from '@/components/monitoring/monitoring-dashboard';

export default async function MonitoringPage() {
  const session = await getServerSession(authOptions);

  // 管理者のみアクセス可能
  if (!session?.user || !session.user.is_superuser) {
    redirect('/dashboard');
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Suspense fallback={
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading monitoring dashboard...</p>
          </div>
        </div>
      }>
        <MonitoringDashboard />
      </Suspense>
    </div>
  );
}
