import { apiClient, ApiError, ApiResponse } from '@/lib/api-client';
import { useCallback, useState } from 'react';
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
    onError: options.onError
      ? (error: Error) => {
          if ('status' in error && 'timestamp' in error) {
            options.onError!(error as ApiError);
          }
        }
      : undefined,
  });

  const execute = useCallback(
    async <R = T>(
      apiCall: () => Promise<ApiResponse<R>>
    ): Promise<R | null> => {
      setState(prev => ({ ...prev, loading: true, error: null }));

      try {
        const response = await apiCall();

        if (!response.error && response.data !== undefined) {
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
          const apiError = new ApiError(response.error, 400, response);
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

        return null;
      } catch (error) {
        const apiError = new ApiError(
          error instanceof Error ? error.message : 'Unknown error',
          500
        );

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
    },
    [options, handleError]
  );

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

  const get = useCallback(
    (endpoint: string) => {
      return api.execute(() => apiClient.request<T>(endpoint));
    },
    [api]
  );

  const post = useCallback(
    (endpoint: string, data?: any) => {
      return api.execute(() =>
        apiClient.request<T>(endpoint, {
          method: 'POST',
          body: JSON.stringify(data),
        })
      );
    },
    [api]
  );

  const put = useCallback(
    (endpoint: string, data?: any) => {
      return api.execute(() =>
        apiClient.request<T>(endpoint, {
          method: 'PUT',
          body: JSON.stringify(data),
        })
      );
    },
    [api]
  );

  const del = useCallback(
    (endpoint: string) => {
      return api.execute(() =>
        apiClient.request<T>(endpoint, {
          method: 'DELETE',
        })
      );
    },
    [api]
  );

  return {
    ...api,
    get,
    post,
    put,
    delete: del,
  };
}
