import { SecurityUtils, apiRateLimiter } from "./security";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export class ApiError extends Error {
  public status: number;
  public response?: ApiResponse;

  constructor(message: string, status: number, response?: ApiResponse) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.response = response;
  }
}

export class ApiClient {
  private baseURL: string;
  private csrfToken: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async getCSRFToken(): Promise<string> {
    if (!this.csrfToken) {
      this.csrfToken = await SecurityUtils.getCSRFToken();
    }
    return this.csrfToken;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    // Check rate limit
    if (!apiRateLimiter.isAllowed()) {
      return {
        error: "Rate limit exceeded. Please try again later.",
      };
    }

    const url = `${this.baseURL}${endpoint}`;

    // Get security headers
    const sessionId = SecurityUtils.getSessionId();
    const csrfToken = await this.getCSRFToken();

    const defaultHeaders = {
      "Content-Type": "application/json",
      "X-Session-ID": sessionId || "",
      "X-CSRF-Token": csrfToken,
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      credentials: "include", // Include cookies for authentication
    };

    try {
      const response = await fetch(url, config);

      // Handle different response types
      if (response.status === 429) {
        return {
          error: "Rate limit exceeded. Please try again later.",
        };
      }

      if (response.status === 403) {
        return {
          error: "Access forbidden. Please check your permissions.",
        };
      }

      if (response.status === 401) {
        // Clear session on unauthorized
        SecurityUtils.clearSession();
        return {
          error: "Authentication required. Please log in again.",
        };
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error("API request failed:", error);
      return {
        error: error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    return this.request("/health");
  }

  // AI Analysis
  async analyzeContent(prompt: string): Promise<ApiResponse<{ analysis: string }>> {
    return this.request("/ai/analyze", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    });
  }

  // Content Generation
  async generateContent(type: string, topic: string): Promise<ApiResponse<{ content: string }>> {
    return this.request("/ai/generate", {
      method: "POST",
      body: JSON.stringify({ type, topic }),
    });
  }

  // Articles
  async getArticles(params?: {
    category?: string;
    sortBy?: string;
    search?: string;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ articles: any[]; total: number }>> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.append("category", params.category);
    if (params?.sortBy) searchParams.append("sortBy", params.sortBy);
    if (params?.search) searchParams.append("search", params.search);
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.limit) searchParams.append("limit", params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/articles?${queryString}` : "/articles";

    return this.request(endpoint);
  }

  async getArticle(id: string): Promise<ApiResponse<any>> {
    return this.request(`/articles/${id}`);
  }

  // Newsletters
  async getNewsletters(params?: {
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ newsletters: any[]; total: number }>> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.limit) searchParams.append("limit", params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/newsletters?${queryString}` : "/newsletters";

    return this.request(endpoint);
  }

  async getNewsletter(id: string): Promise<ApiResponse<any>> {
    return this.request(`/newsletters/${id}`);
  }

  // Trends
  async getTrends(params?: {
    timeframe?: string;
    category?: string;
    sortBy?: string;
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ trends: any[]; total: number }>> {
    const searchParams = new URLSearchParams();
    if (params?.timeframe) searchParams.append("timeframe", params.timeframe);
    if (params?.category) searchParams.append("category", params.category);
    if (params?.sortBy) searchParams.append("sortBy", params.sortBy);
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.limit) searchParams.append("limit", params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/trends?${queryString}` : "/trends";

    return this.request(endpoint);
  }

  async getTrend(id: string): Promise<ApiResponse<any>> {
    return this.request(`/trends/${id}`);
  }

  // Collection Jobs
  async getCollectionJobs(): Promise<ApiResponse<{ jobs: any[] }>> {
    return this.request("/collection/jobs");
  }

  async createCollectionJob(config: any): Promise<ApiResponse<{ job: any }>> {
    return this.request("/collection/jobs", {
      method: "POST",
      body: JSON.stringify(config),
    });
  }

  async getCollectionJob(id: string): Promise<ApiResponse<any>> {
    return this.request(`/collection/jobs/${id}`);
  }

  // Analysis Results
  async getAnalysisResults(params?: {
    page?: number;
    limit?: number;
  }): Promise<ApiResponse<{ results: any[]; total: number }>> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.append("page", params.page.toString());
    if (params?.limit) searchParams.append("limit", params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/analysis/results?${queryString}` : "/analysis/results";

    return this.request(endpoint);
  }

  async getAnalysisResult(id: string): Promise<ApiResponse<any>> {
    return this.request(`/analysis/results/${id}`);
  }

  // Content Recommendations
  async getRecommendations(
    userId: string,
    limit: number = 10,
  ): Promise<ApiResponse<{ recommendations: any[]; count: number }>> {
    return this.request(`/content-quality/recommendations/${userId}?limit=${limit}`);
  }

  async getSimilarContent(
    contentId: string,
    limit: number = 5,
  ): Promise<ApiResponse<{ similar_contents: any[]; count: number }>> {
    return this.request(`/content-quality/similar/${contentId}?limit=${limit}`);
  }

  async getTrendingContent(
    category?: string,
    limit: number = 10,
  ): Promise<ApiResponse<{ trending_contents: any[]; count: number }>> {
    const query = category ? `?category=${category}&limit=${limit}` : `?limit=${limit}`;
    return this.request(`/content-quality/trending${query}`);
  }

  async getUserBehaviorAnalytics(params?: {
    startDate?: string;
    endDate?: string;
    affiliateId?: number;
  }): Promise<ApiResponse<{ success: boolean; analytics: any }>> {
    const searchParams = new URLSearchParams();
    if (params?.startDate) searchParams.append("start_date", params.startDate);
    if (params?.endDate) searchParams.append("end_date", params.endDate);
    if (params?.affiliateId) searchParams.append("affiliate_id", params.affiliateId.toString());

    const suffix = searchParams.toString() ? `?${searchParams.toString()}` : "";
    return this.request(`/api/analytics/user-behavior${suffix}`);
  }

  async getArticlePerformanceDetail(params: {
    articleId: string;
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<{ success: boolean; performance: any }>> {
    const searchParams = new URLSearchParams();
    if (params.startDate) searchParams.append("start_date", params.startDate);
    if (params.endDate) searchParams.append("end_date", params.endDate);

    const suffix = searchParams.toString() ? `?${searchParams.toString()}` : "";
    return this.request(
      `/api/analytics/article-performance/${encodeURIComponent(params.articleId)}${suffix}`,
    );
  }

  async getArticleRankings(params?: {
    startDate?: string;
    endDate?: string;
    sortBy?: "page_views" | "engagement" | "conversions";
    limit?: number;
  }): Promise<ApiResponse<{ success: boolean; rankings: any }>> {
    const searchParams = new URLSearchParams();
    if (params?.startDate) searchParams.append("start_date", params.startDate);
    if (params?.endDate) searchParams.append("end_date", params.endDate);
    if (params?.sortBy) searchParams.append("sort_by", params.sortBy);
    if (params?.limit) searchParams.append("limit", params.limit.toString());

    const suffix = searchParams.toString() ? `?${searchParams.toString()}` : "";
    return this.request(`/api/analytics/article-rankings${suffix}`);
  }

  async recordInteraction(
    userId: string,
    contentId: string,
    interactionType: "view" | "like" | "share" | "bookmark",
    metadata?: Record<string, any>,
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request("/content-quality/interaction", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        content_id: contentId,
        interaction_type: interactionType,
        metadata,
      }),
    });
  }

  // Affiliate API methods
  async registerAffiliate(
    userId: string,
  ): Promise<ApiResponse<{ success: boolean; affiliate: any }>> {
    return this.request("/api/affiliate/register", {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    });
  }

  async getAffiliateProfile(
    userId: string,
  ): Promise<ApiResponse<{ success: boolean; affiliate: any; stats: any }>> {
    return this.request(`/api/affiliate/profile/${userId}`);
  }

  async getReferralLinks(
    affiliateId: number,
    activeOnly: boolean = true,
  ): Promise<ApiResponse<{ success: boolean; links: any[]; count: number }>> {
    const query = `?active_only=${activeOnly}`;
    return this.request(`/api/affiliate/referral-links/${affiliateId}${query}`);
  }

  async createReferralLink(data: {
    affiliate_id: number;
    destination_url: string;
    campaign_name?: string;
    valid_until?: string;
  }): Promise<ApiResponse<{ success: boolean; link: any }>> {
    return this.request("/api/affiliate/referral-links", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getAffiliateStats(
    affiliateId: number,
  ): Promise<ApiResponse<{ success: boolean; stats: any }>> {
    return this.request(`/api/affiliate/stats/${affiliateId}`);
  }

  async getPayouts(
    affiliateId: number,
    limit: number = 50,
  ): Promise<ApiResponse<{ success: boolean; payouts: any[]; count: number }>> {
    return this.request(`/api/affiliate/payouts/${affiliateId}?limit=${limit}`);
  }

  async getTopAffiliates(
    limit: number = 20,
    orderBy: string = "total_revenue",
  ): Promise<ApiResponse<{ success: boolean; affiliates: any[]; count: number }>> {
    const query = `?limit=${limit}&order_by=${orderBy}`;
    return this.request(`/api/affiliate/top-affiliates${query}`);
  }

  async getAllReferralLinks(
    activeOnly: boolean = true,
    limit: number = 100,
  ): Promise<ApiResponse<{ success: boolean; links: any[]; count: number }>> {
    const query = `?active_only=${activeOnly}&limit=${limit}`;
    return this.request(`/api/affiliate/admin/referral-links${query}`);
  }

  async updateReferralLink(
    linkId: number,
    data: { is_active?: boolean; valid_until?: string },
  ): Promise<ApiResponse<{ success: boolean; link: any }>> {
    return this.request(`/api/affiliate/referral-links/${linkId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async getClickStatistics(params: {
    affiliate_id?: number;
    link_id?: number;
  }): Promise<ApiResponse<{ success: boolean; statistics: any }>> {
    const query = new URLSearchParams();
    if (params.affiliate_id) query.set("affiliate_id", params.affiliate_id.toString());
    if (params.link_id) query.set("link_id", params.link_id.toString());
    const suffix = query.toString() ? `?${query.toString()}` : "";
    return this.request(`/api/affiliate/admin/click-statistics${suffix}`);
  }
}

// Singleton instance
export const apiClient = new ApiClient();
