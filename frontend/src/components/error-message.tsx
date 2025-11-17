import { AlertCircle, X, RefreshCw } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";

interface ErrorMessageProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
  variant?: "default" | "destructive" | "warning";
  showDetails?: boolean;
  details?: string;
}

export function ErrorMessage({
  title = "エラーが発生しました",
  message,
  onRetry,
  onDismiss,
  variant = "destructive",
  showDetails = false,
  details,
}: ErrorMessageProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case "destructive":
        return "border-red-200 bg-red-50 text-red-800";
      case "warning":
        return "border-yellow-200 bg-yellow-50 text-yellow-800";
      default:
        return "border-gray-200 bg-gray-50 text-gray-800";
    }
  };

  const getIconColor = () => {
    switch (variant) {
      case "destructive":
        return "text-red-600";
      case "warning":
        return "text-yellow-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <Card className={`border ${getVariantStyles()}`}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className={`h-5 w-5 mt-0.5 flex-shrink-0 ${getIconColor()}`} />

          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-sm mb-1">{title}</h3>
            <p className="text-sm mb-3">{message}</p>

            {showDetails && details && (
              <details className="mb-3">
                <summary className="text-xs cursor-pointer hover:underline">詳細を表示</summary>
                <pre className="mt-2 text-xs bg-white/50 p-2 rounded border overflow-auto">
                  {details}
                </pre>
              </details>
            )}

            <div className="flex gap-2">
              {onRetry && (
                <Button size="sm" variant="outline" onClick={onRetry} className="text-xs">
                  <RefreshCw className="h-3 w-3 mr-1" />
                  再試行
                </Button>
              )}

              {onDismiss && (
                <Button size="sm" variant="ghost" onClick={onDismiss} className="text-xs">
                  <X className="h-3 w-3 mr-1" />
                  閉じる
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
