import { useState, useCallback } from 'react';
import { apiClient, ApiResponse, ApiError } from '@/lib/api-client';
import { useErrorHandler } from './use-error-handler';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: ApiError) => void;
  showErrorToast?: boolean;
}

export function useApi<T = any>(options: UseApiOptions = {}) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const { handleError } = useErrorHandler({
    onError: options.onError,
  });

  const execute = useCallback(async <R = T>(
    apiCall: () => Promise<ApiResponse<R>>
  ): Promise<R | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const response = await apiCall();

      if (response.success && response.data !== undefined) {
        setState({
          data: response.data as T,
          loading: false,
          error: null,
        });

        if (options.onSuccess) {
          options.onSuccess(response.data);
        }

        return response.data;
      } else if (response.error) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: response.error!,
        }));

        if (options.onError) {
          options.onError(response.error);
        } else {
          handleError(response.error.message);
        }

        return null;
      }

      return null;
    } catch (error) {
      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Unknown error',
        code: 'INTERNAL_SERVER_ERROR',
        status: 0,
        timestamp: new Date().toISOString(),
      };

      setState(prev => ({
        ...prev,
        loading: false,
        error: apiError,
      }));

      if (options.onError) {
        options.onError(apiError);
      } else {
        handleError(apiError.message);
      }

      return null;
    }
  }, [options, handleError]);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

// 特定のAPI呼び出し用のフック
export function useApiCall<T = any>(options: UseApiOptions = {}) {
  const api = useApi<T>(options);

  const get = useCallback((endpoint: string) => {
    return api.execute(() => apiClient.get<T>(endpoint));
  }, [api]);

  const post = useCallback((endpoint: string, data?: any) => {
    return api.execute(() => apiClient.post<T>(endpoint, data));
  }, [api]);

  const put = useCallback((endpoint: string, data?: any) => {
    return api.execute(() => apiClient.put<T>(endpoint, data));
  }, [api]);

  const del = useCallback((endpoint: string) => {
    return api.execute(() => apiClient.delete<T>(endpoint));
  }, [api]);

  return {
    ...api,
    get,
    post,
    put,
    delete: del,
  };
}
