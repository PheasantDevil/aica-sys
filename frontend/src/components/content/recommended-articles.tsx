"use client";

import { apiClient } from "@/lib/api-client";
import Link from "next/link";
import { useEffect, useState } from "react";

interface RecommendedArticle {
  id: number;
  title: string;
  slug: string;
  summary: string;
  score?: number;
  similarity?: number;
  published_at?: string;
}

interface RecommendedArticlesProps {
  contentId: string;
  userId?: string;
  type?: "similar" | "trending" | "personalized";
  limit?: number;
  title?: string;
}

export function RecommendedArticles({
  contentId,
  userId,
  type = "similar",
  limit = 5,
  title,
}: RecommendedArticlesProps) {
  const [articles, setArticles] = useState<RecommendedArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRecommendations() {
      try {
        setLoading(true);
        setError(null);

        let response;
        if (type === "similar") {
          response = await apiClient.getSimilarContent(contentId, limit);
          if (response.data) {
            setArticles(response.data.similar_contents || []);
          } else if (response.error) {
            setError(response.error);
          }
        } else if (type === "trending") {
          response = await apiClient.getTrendingContent(undefined, limit);
          if (response.data) {
            setArticles(response.data.trending_contents || []);
          } else if (response.error) {
            setError(response.error);
          }
        } else if (type === "personalized" && userId) {
          response = await apiClient.getRecommendations(userId, limit);
          if (response.data) {
            setArticles(response.data.recommendations || []);
          } else if (response.error) {
            setError(response.error);
          }
        }
      } catch (err) {
        console.error("Failed to fetch recommendations:", err);
        setError("推薦記事の取得に失敗しました");
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, [contentId, userId, type, limit]);

  if (loading) {
    return (
      <section className="mt-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">{title || "おすすめ記事"}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: limit }).map((_, i) => (
            <div key={i} className="animate-pulse bg-gray-200 rounded-lg h-64" />
          ))}
        </div>
      </section>
    );
  }

  if (error || articles.length === 0) {
    return null; // エラー時や記事がない場合は何も表示しない
  }

  return (
    <section className="mt-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">{title || "おすすめ記事"}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article) => (
          <Link key={article.id} href={`/articles/${article.slug}`} className="block">
            <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 h-full">
              <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {article.title}
              </h3>
              <p className="text-sm text-gray-600 mb-4 line-clamp-3">{article.summary}</p>
              {article.published_at && (
                <p className="text-xs text-gray-500">
                  {new Date(article.published_at).toLocaleDateString("ja-JP")}
                </p>
              )}
              {(article.score !== undefined || article.similarity !== undefined) && (
                <div className="mt-2 text-xs text-blue-600">
                  {type === "similar" && article.similarity !== undefined
                    ? `類似度: ${(article.similarity * 100).toFixed(0)}%`
                    : article.score !== undefined
                    ? `スコア: ${article.score.toFixed(1)}`
                    : null}
                </div>
              )}
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
