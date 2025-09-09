import { ApiResponse, ApiError, ErrorCode, ERROR_MESSAGES } from '@/types/api';

class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');

    if (!response.ok) {
      let error: ApiError;
      
      if (isJson) {
        const errorData = await response.json();
        error = {
          message: errorData.message || ERROR_MESSAGES[ErrorCode.INTERNAL_SERVER_ERROR],
          code: errorData.code || ErrorCode.INTERNAL_SERVER_ERROR,
          status: response.status,
          details: errorData.details,
          timestamp: new Date().toISOString(),
        };
      } else {
        error = {
          message: this.getErrorMessageByStatus(response.status),
          code: this.getErrorCodeByStatus(response.status),
          status: response.status,
          timestamp: new Date().toISOString(),
        };
      }

      return {
        success: false,
        error,
      };
    }

    if (isJson) {
      const data = await response.json();
      return {
        success: true,
        data,
      };
    }

    return {
      success: true,
      data: null as T,
    };
  }

  private getErrorMessageByStatus(status: number): string {
    switch (status) {
      case 400:
        return ERROR_MESSAGES[ErrorCode.VALIDATION_ERROR];
      case 401:
        return ERROR_MESSAGES[ErrorCode.UNAUTHORIZED];
      case 403:
        return ERROR_MESSAGES[ErrorCode.FORBIDDEN];
      case 404:
        return ERROR_MESSAGES[ErrorCode.NOT_FOUND];
      case 409:
        return ERROR_MESSAGES[ErrorCode.CONFLICT];
      case 429:
        return ERROR_MESSAGES[ErrorCode.RATE_LIMITED];
      case 500:
      case 502:
      case 503:
      case 504:
        return ERROR_MESSAGES[ErrorCode.INTERNAL_SERVER_ERROR];
      default:
        return ERROR_MESSAGES[ErrorCode.INTERNAL_SERVER_ERROR];
    }
  }

  private getErrorCodeByStatus(status: number): ErrorCode {
    switch (status) {
      case 400:
        return ErrorCode.VALIDATION_ERROR;
      case 401:
        return ErrorCode.UNAUTHORIZED;
      case 403:
        return ErrorCode.FORBIDDEN;
      case 404:
        return ErrorCode.NOT_FOUND;
      case 409:
        return ErrorCode.CONFLICT;
      case 429:
        return ErrorCode.RATE_LIMITED;
      case 500:
      case 502:
      case 503:
      case 504:
        return ErrorCode.INTERNAL_SERVER_ERROR;
      default:
        return ErrorCode.INTERNAL_SERVER_ERROR;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const config: RequestInit = {
        ...options,
        headers: {
          ...this.defaultHeaders,
          ...options.headers,
        },
      };

      const response = await fetch(url, config);
      return await this.handleResponse<T>(response);
    } catch (error) {
      // ネットワークエラーの処理
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        return {
          success: false,
          error: {
            message: ERROR_MESSAGES[ErrorCode.NETWORK_ERROR],
            code: ErrorCode.NETWORK_ERROR,
            status: 0,
            timestamp: new Date().toISOString(),
          },
        };
      }

      // その他のエラー
      return {
        success: false,
        error: {
          message: error instanceof Error ? error.message : 'Unknown error',
          code: ErrorCode.INTERNAL_SERVER_ERROR,
          status: 0,
          timestamp: new Date().toISOString(),
        },
      };
    }
  }

  async get<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  removeAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }
}

export const apiClient = new ApiClient();
