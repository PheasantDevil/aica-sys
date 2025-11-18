"use client";

import { errorHandler } from "@/lib/error-handler";
import { createContext, ReactNode, useContext, useEffect } from "react";

interface ErrorContextType {
  handleError: (errorData: Partial<any>) => void;
  getErrors: () => any[];
  getErrorsBySeverity: (severity: string) => any[];
  getErrorsByCategory: (category: string) => any[];
  clearErrors: () => void;
  getErrorStats: () => any;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

interface ErrorProviderProps {
  children: ReactNode;
}

export function ErrorProvider({ children }: ErrorProviderProps) {
  useEffect(() => {
    // Load persisted errors from localStorage
    if (typeof window !== "undefined") {
      try {
        const persistedErrors = localStorage.getItem("error_logs");
        if (persistedErrors) {
          const errors = JSON.parse(persistedErrors);
          // Add persisted errors to the error handler
          errors.forEach((error: any) => {
            errorHandler.handleError(error);
          });
        }
      } catch (error) {
        console.warn("Failed to load persisted errors:", error);
      }
    }
  }, []);

  const contextValue: ErrorContextType = {
    handleError: (errorData: Partial<any>) => errorHandler.handleError(errorData),
    getErrors: () => errorHandler.getErrors(),
    getErrorsBySeverity: (severity: string) => errorHandler.getErrorsBySeverity(severity as any),
    getErrorsByCategory: (category: string) => errorHandler.getErrorsByCategory(category as any),
    clearErrors: () => errorHandler.clearErrors(),
    getErrorStats: () => errorHandler.getErrorStats(),
  };

  return <ErrorContext.Provider value={contextValue}>{children}</ErrorContext.Provider>;
}

export function useError() {
  const context = useContext(ErrorContext);
  if (context === undefined) {
    throw new Error("useError must be used within an ErrorProvider");
  }
  return context;
}
