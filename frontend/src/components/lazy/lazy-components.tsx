'use client';

import { Loading } from '@/components/ui/loading';
import dynamic from 'next/dynamic';
import React, { ComponentType } from 'react';

// Lazy loading wrapper with loading state
export function createLazyComponent<T = {}>(
  importFunc: () => Promise<any>,
  fallback?: ComponentType
) {
  return dynamic(importFunc, {
    loading: fallback ? () => React.createElement(fallback) : () => <Loading />,
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
// Note: These components will be implemented in future phases
