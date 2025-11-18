import { useCallback, useState } from "react";

export interface ErrorState {
  hasError: boolean;
  error: Error | null;
  message: string;
}

export interface ErrorHandlerOptions {
  onError?: (error: Error) => void;
  fallbackMessage?: string;
  logError?: boolean;
}

export function useErrorHandler(options: ErrorHandlerOptions = {}) {
  const [errorState, setErrorState] = useState<ErrorState>({
    hasError: false,
    error: null,
    message: "",
  });

  const handleError = useCallback(
    (error: Error | string, customMessage?: string) => {
      const errorObj = typeof error === "string" ? new Error(error) : error;
      const message =
        customMessage || errorObj.message || options.fallbackMessage || "エラーが発生しました";

      setErrorState({
        hasError: true,
        error: errorObj,
        message,
      });

      // エラーログの出力
      if (options.logError !== false) {
        console.error("Error handled by useErrorHandler:", errorObj);
      }

      // カスタムエラーハンドラー
      if (options.onError) {
        options.onError(errorObj);
      }
    },
    [options],
  );

  const clearError = useCallback(() => {
    setErrorState({
      hasError: false,
      error: null,
      message: "",
    });
  }, []);

  const handleAsyncError = useCallback(
    async <T>(asyncFn: () => Promise<T>, customMessage?: string): Promise<T | null> => {
      try {
        return await asyncFn();
      } catch (error) {
        handleError(error as Error, customMessage);
        return null;
      }
    },
    [handleError],
  );

  return {
    errorState,
    handleError,
    clearError,
    handleAsyncError,
  };
}
