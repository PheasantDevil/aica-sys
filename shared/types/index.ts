/**
 * Shared TypeScript types for AICA-SyS
 * AI-driven Content Curation & Automated Sales System
 */

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  subscriptionStatus: SubscriptionStatus;
  createdAt: Date;
  updatedAt: Date;
}

export enum SubscriptionStatus {
  FREE = 'free',
  PREMIUM = 'premium',
  CANCELLED = 'cancelled'
}

// Content types
export interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  tags: string[];
  publishedAt: Date;
  author: string;
  readTime: number;
  isPremium: boolean;
  views: number;
  likes: number;
}

export interface Newsletter {
  id: string;
  title: string;
  content: string;
  publishedAt: Date;
  subscribers: number;
  openRate: number;
}

export interface Trend {
  id: string;
  title: string;
  description: string;
  category: TrendCategory;
  impact: TrendImpact;
  relatedArticles: string[];
  createdAt: Date;
}

export enum TrendCategory {
  FRAMEWORK = 'framework',
  LIBRARY = 'library',
  TOOL = 'tool',
  LANGUAGE = 'language',
  ECOSYSTEM = 'ecosystem'
}

export enum TrendImpact {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// AI Agent types
export interface CollectionJob {
  id: string;
  source: string;
  type: CollectionType;
  status: JobStatus;
  startedAt: Date;
  completedAt?: Date;
  error?: string;
  itemsCollected: number;
}

export enum CollectionType {
  GITHUB = 'github',
  RSS = 'rss',
  WEB_SCRAPING = 'web_scraping',
  API = 'api'
}

export enum JobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

export interface AnalysisResult {
  id: string;
  sourceId: string;
  title: string;
  summary: string;
  keyPoints: string[];
  sentiment: Sentiment;
  relevance: number;
  createdAt: Date;
}

export enum Sentiment {
  POSITIVE = 'positive',
  NEUTRAL = 'neutral',
  NEGATIVE = 'negative'
}

// Payment types
export interface Subscription {
  id: string;
  userId: string;
  plan: SubscriptionPlan;
  status: SubscriptionStatus;
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  cancelAtPeriodEnd: boolean;
  stripeSubscriptionId: string;
}

export enum SubscriptionPlan {
  FREE = 'free',
  PREMIUM_MONTHLY = 'premium_monthly',
  PREMIUM_YEARLY = 'premium_yearly'
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Search and filter types
export interface SearchFilters {
  query?: string;
  tags?: string[];
  category?: TrendCategory;
  dateFrom?: Date;
  dateTo?: Date;
  isPremium?: boolean;
}

export interface SortOptions {
  field: string;
  direction: 'asc' | 'desc';
}
