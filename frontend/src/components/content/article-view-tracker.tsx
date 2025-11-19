"use client";

import { apiClient } from "@/lib/api-client";
import { useEffect } from "react";

interface ArticleViewTrackerProps {
  articleId: string;
  userId?: string;
  metadata?: Record<string, any>;
}

export function ArticleViewTracker({ articleId, userId, metadata }: ArticleViewTrackerProps) {
  useEffect(() => {
    // セッションIDを取得（ユーザーIDがない場合）
    const sessionId = userId || `session_${Date.now()}`;

    // 閲覧履歴を記録
    async function recordView() {
      try {
        await apiClient.recordInteraction(sessionId, articleId, "view", {
          ...metadata,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
          referrer: document.referrer,
        });
      } catch (error) {
        console.error("Failed to record article view:", error);
      }
    }

    // ページ表示時に記録
    recordView();
  }, [articleId, userId, metadata]);

  return null; // このコンポーネントは何も表示しない
}
