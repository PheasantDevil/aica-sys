'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { useState } from 'react';

interface Subscription {
  id: string;
  userId: string;
  stripeCustomerId: string | null;
  stripeSubscriptionId: string | null;
  stripePriceId: string | null;
  stripeCurrentPeriodEnd: Date | null;
  status: string;
  plan: string;
  createdAt: Date;
  updatedAt: Date;
}

export function useSubscription() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  const [isLoading, setIsLoading] = useState(false);

  const {
    data: subscription,
    isLoading: isSubscriptionLoading,
    error: subscriptionError,
  } = useQuery({
    queryKey: ['subscription', session?.user?.id],
    queryFn: async (): Promise<Subscription | null> => {
      if (!session?.user?.id) return null;
      
      const response = await fetch('/api/subscription');
      if (!response.ok) {
        throw new Error('Failed to fetch subscription');
      }
      return response.json();
    },
    enabled: !!session?.user?.id,
  });

  const createCheckoutMutation = useMutation({
    mutationFn: async (priceId: string) => {
      const response = await fetch('/api/stripe/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ priceId }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { url } = await response.json();
      return url;
    },
    onSuccess: (url) => {
      window.location.href = url;
    },
  });

  const handleUpgrade = async (priceId: string) => {
    setIsLoading(true);
    try {
      await createCheckoutMutation.mutateAsync(priceId);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContact = () => {
    // エンタープライズプランのお問い合わせ処理
    window.open('mailto:sales@aica-sys.com?subject=エンタープライズプランについて', '_blank');
  };

  return {
    subscription,
    isLoading: isSubscriptionLoading || isLoading,
    error: subscriptionError,
    handleUpgrade,
    handleContact,
    isUpgrading: createCheckoutMutation.isPending,
  };
}
