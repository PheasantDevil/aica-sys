export interface ApiError {
  message: string;
  code?: string;
  status: number;
  details?: Record<string, any>;
  timestamp: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: ApiError;
  success: boolean;
  message?: string;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface ApiErrorResponse {
  message: string;
  code: string;
  status: number;
  validationErrors?: ValidationError[];
  timestamp: string;
}

// エラーコードの定義
export enum ErrorCode {
  VALIDATION_ERROR = "VALIDATION_ERROR",
  UNAUTHORIZED = "UNAUTHORIZED",
  FORBIDDEN = "FORBIDDEN",
  NOT_FOUND = "NOT_FOUND",
  CONFLICT = "CONFLICT",
  INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR",
  NETWORK_ERROR = "NETWORK_ERROR",
  TIMEOUT = "TIMEOUT",
  RATE_LIMITED = "RATE_LIMITED",
}

// エラーメッセージのマッピング
export const ERROR_MESSAGES: Record<ErrorCode, string> = {
  [ErrorCode.VALIDATION_ERROR]: "入力内容に問題があります",
  [ErrorCode.UNAUTHORIZED]: "ログインが必要です",
  [ErrorCode.FORBIDDEN]: "アクセス権限がありません",
  [ErrorCode.NOT_FOUND]: "リソースが見つかりません",
  [ErrorCode.CONFLICT]: "データの競合が発生しました",
  [ErrorCode.INTERNAL_SERVER_ERROR]: "サーバーエラーが発生しました",
  [ErrorCode.NETWORK_ERROR]: "ネットワークエラーが発生しました",
  [ErrorCode.TIMEOUT]: "リクエストがタイムアウトしました",
  [ErrorCode.RATE_LIMITED]: "リクエスト制限に達しました",
};
