import React, { ReactElement } from "react";
import { render, RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { SessionProvider } from "next-auth/react";

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <SessionProvider session={null}>{children}</SessionProvider>
    </QueryClientProvider>
  );
};

const customRender = (ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) =>
  render(ui, { wrapper: AllTheProviders, ...options });

// Mock data for testing
export const mockArticles = [
  {
    id: "1",
    title: "Test Article 1",
    description: "Test description 1",
    content: "Test content 1",
    author: {
      name: "Test Author",
      avatar: "/test-avatar.jpg",
    },
    category: "tutorial",
    tags: ["TypeScript", "Test"],
    publishedAt: "2024-01-15T10:00:00Z",
    readTime: 5,
    views: 100,
    likes: 10,
    isPremium: false,
    imageUrl: "/test-image.jpg",
  },
];

export const mockNewsletters = [
  {
    id: "1",
    title: "Test Newsletter 1",
    description: "Test newsletter description",
    content: "Test newsletter content",
    publishedAt: "2024-01-15T10:00:00Z",
    subscribers: 1000,
    openRate: 75,
    clickRate: 25,
    isPremium: false,
    imageUrl: "/test-newsletter.jpg",
    tags: ["TypeScript", "Newsletter"],
  },
];

export const mockTrends = [
  {
    id: "1",
    title: "Test Trend 1",
    description: "Test trend description",
    category: "libraries",
    tags: ["TypeScript", "Trend"],
    publishedAt: "2024-01-15T10:00:00Z",
    trendScore: 85,
    changeRate: 25,
    engagement: 80,
    isPremium: false,
    imageUrl: "/test-trend.jpg",
    metrics: {
      mentions: 500,
      growth: 25,
      sentiment: "positive" as const,
    },
  },
];

export const mockUser = {
  id: "1",
  name: "Test User",
  email: "test@example.com",
  image: "/test-user.jpg",
};

export const mockSubscription = {
  id: "1",
  userId: "1",
  stripeCustomerId: "cus_test",
  stripeSubscriptionId: "sub_test",
  stripePriceId: "price_test",
  stripeCurrentPeriodEnd: new Date("2024-02-15T10:00:00Z"),
  status: "active",
  plan: "premium",
  createdAt: new Date("2024-01-15T10:00:00Z"),
  updatedAt: new Date("2024-01-15T10:00:00Z"),
};

// Helper functions
export const createMockSession = (overrides = {}) => ({
  user: mockUser,
  expires: "2024-12-31T23:59:59.999Z",
  ...overrides,
});

export const createMockQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

// Re-export everything
export * from "@testing-library/react";
export { customRender as render };
