import { lazy, Suspense } from 'react';

// ダッシュボードコンポーネントの遅延読み込み
export const LazyDashboard = lazy(() => import('./dashboard-nav'));

// 重いコンポーネントの遅延読み込み
export const LazyPricing = lazy(() => import('./pricing'));
export const LazyFeatures = lazy(() => import('./features'));
export const LazyHero = lazy(() => import('./hero'));

// ローディングコンポーネント
export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className="flex items-center justify-center p-4">
      <div
        className={`${sizeClasses[size]} border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin`}
      ></div>
    </div>
  );
}

// 遅延読み込み用のラッパーコンポーネント
export function LazyWrapper({
  children,
  fallback,
}: {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  return (
    <Suspense fallback={fallback || <LoadingSpinner />}>
      {children}
    </Suspense>
  );
}
