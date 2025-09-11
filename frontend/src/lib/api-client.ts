const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    return this.request('/health');
  }

  // AI Analysis
  async analyzeContent(prompt: string): Promise<ApiResponse<{ analysis: string }>> {
    return this.request('/ai/analyze', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  // Content Generation
  async generateContent(type: string, topic: string): Promise<ApiResponse<{ content: string }>> {
    return this.request('/ai/generate', {
      method: 'POST',
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
    if (params?.category) searchParams.append('category', params.category);
    if (params?.sortBy) searchParams.append('sortBy', params.sortBy);
    if (params?.search) searchParams.append('search', params.search);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/articles?${queryString}` : '/articles';
    
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
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/newsletters?${queryString}` : '/newsletters';
    
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
    if (params?.timeframe) searchParams.append('timeframe', params.timeframe);
    if (params?.category) searchParams.append('category', params.category);
    if (params?.sortBy) searchParams.append('sortBy', params.sortBy);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/trends?${queryString}` : '/trends';
    
    return this.request(endpoint);
  }

  async getTrend(id: string): Promise<ApiResponse<any>> {
    return this.request(`/trends/${id}`);
  }

  // Collection Jobs
  async getCollectionJobs(): Promise<ApiResponse<{ jobs: any[] }>> {
    return this.request('/collection/jobs');
  }

  async createCollectionJob(config: any): Promise<ApiResponse<{ job: any }>> {
    return this.request('/collection/jobs', {
      method: 'POST',
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
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const queryString = searchParams.toString();
    const endpoint = queryString ? `/analysis/results?${queryString}` : '/analysis/results';
    
    return this.request(endpoint);
  }

  async getAnalysisResult(id: string): Promise<ApiResponse<any>> {
    return this.request(`/analysis/results/${id}`);
  }
}

// Singleton instance
export const apiClient = new ApiClient();