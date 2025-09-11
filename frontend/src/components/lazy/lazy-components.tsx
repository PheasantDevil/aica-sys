'use client';

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';
import { Loading } from '@/components/ui/loading';

// Lazy loading wrapper with loading state
export function createLazyComponent<T = {}>(
  importFunc: () => Promise<{ default: ComponentType<T> }>,
  fallback?: ComponentType
) {
  return dynamic(importFunc, {
    loading: fallback ? () => <fallback /> : () => <Loading />,
    ssr: false,
  });
}

// Pre-configured lazy components
export const LazyArticleCard = createLazyComponent(
  () => import('@/components/content/article-card'),
  () => <Loading />
);

export const LazyNewsletterCard = createLazyComponent(
  () => import('@/components/content/newsletter-card'),
  () => <Loading />
);

export const LazyTrendCard = createLazyComponent(
  () => import('@/components/content/trend-card'),
  () => <Loading />
);

export const LazyDashboardOverview = createLazyComponent(
  () => import('@/components/dashboard/dashboard-overview'),
  () => <Loading />
);

export const LazySubscriptionCard = createLazyComponent(
  () => import('@/components/subscription/subscription-card'),
  () => <Loading />
);

export const LazyCheckoutForm = createLazyComponent(
  () => import('@/components/payment/checkout-form'),
  () => <Loading />
);

export const LazySettings = createLazyComponent(
  () => import('@/components/settings/profile-settings'),
  () => <Loading />
);

// Heavy components that should be lazy loaded
export const LazyChart = createLazyComponent(
  () => import('@/components/ui/chart'),
  () => <div className="h-64 bg-muted animate-pulse rounded" />
);

export const LazyDataTable = createLazyComponent(
  () => import('@/components/ui/data-table'),
  () => <Loading />
);

export const LazyRichTextEditor = createLazyComponent(
  () => import('@/components/ui/rich-text-editor'),
  () => <div className="h-32 bg-muted animate-pulse rounded" />
);
