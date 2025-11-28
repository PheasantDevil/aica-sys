"use client";

import { type ComponentType, useCallback, useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { format } from "date-fns";
import { BarChart3, Eye, Heart, MessageSquare, Share2, TrendingUp } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";

const LineChartSafe = LineChart as unknown as ComponentType<any>;
const LineSafe = Line as unknown as ComponentType<any>;
const CartesianGridSafe = CartesianGrid as unknown as ComponentType<any>;
const XAxisSafe = XAxis as unknown as ComponentType<any>;
const YAxisSafe = YAxis as unknown as ComponentType<any>;
const TooltipSafe = Tooltip as unknown as ComponentType<any>;
const LegendSafe = Legend as unknown as ComponentType<any>;
const ResponsiveContainerSafe = ResponsiveContainer as unknown as ComponentType<any>;

interface ArticleRanking {
  article_id: string;
  article_title: string;
  article_published_at: string | null;
  metrics: {
    page_views: number;
    unique_users: number;
    likes: number;
    shares: number;
    comments: number;
    conversions: number;
    engagement_rate: number;
    conversion_rate: number;
  };
}

interface ArticlePerformance {
  article_id: string;
  article_title: string;
  article_published_at: string | null;
  period: {
    start: string;
    end: string;
  };
  metrics: {
    page_views: number;
    unique_users: number;
    average_time_on_page: number;
    engagement_rate: number;
    conversion_rate: number;
  };
  engagement: {
    likes: number;
    shares: number;
    comments: number;
  };
  trend: Array<{
    date: string;
    page_views: number;
    likes: number;
    shares: number;
    comments: number;
    conversions: number;
  }>;
}

const numberFormatter = new Intl.NumberFormat("ja-JP");

function formatSeconds(seconds: number): string {
  if (!seconds || seconds <= 0) {
    return "0秒";
  }
  if (seconds < 60) {
    return `${seconds.toFixed(0)}秒`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}分${remainingSeconds}秒`;
}

export function AdminContentPerformance() {
  const [rankings, setRankings] = useState<ArticleRanking[]>([]);
  const [selectedArticleId, setSelectedArticleId] = useState<string | null>(null);
  const [articlePerformance, setArticlePerformance] = useState<ArticlePerformance | null>(null);
  const [sortBy, setSortBy] = useState<"page_views" | "engagement" | "conversions">("page_views");
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date }>({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    end: new Date(),
  });

  const { loading: rankingsLoading, execute: executeRankings } = useApiCall<{
    success: boolean;
    rankings: { rankings: ArticleRanking[] };
  }>();

  const { loading: detailLoading, execute: executeDetail } = useApiCall<{
    success: boolean;
    performance: ArticlePerformance;
  }>();

  const loadRankings = useCallback(async () => {
    const result = await executeRankings(() =>
      apiClient.getArticleRankings({
        startDate: dateRange.start.toISOString(),
        endDate: dateRange.end.toISOString(),
        sortBy,
        limit: 50,
      }),
    );

    if (result?.success && result.rankings?.rankings) {
      setRankings(result.rankings.rankings);
    }
  }, [dateRange, sortBy, executeRankings]);

  const loadArticleDetail = useCallback(
    async (articleId: string) => {
      const result = await executeDetail(() =>
        apiClient.getArticlePerformanceDetail({
          articleId,
          startDate: dateRange.start.toISOString(),
          endDate: dateRange.end.toISOString(),
        }),
      );

      if (result?.success && result.performance) {
        setArticlePerformance(result.performance);
      }
    },
    [dateRange, executeDetail],
  );

  useEffect(() => {
    loadRankings();
  }, [loadRankings]);

  useEffect(() => {
    if (selectedArticleId) {
      loadArticleDetail(selectedArticleId);
    }
  }, [selectedArticleId, loadArticleDetail]);

  const chartData = useMemo(() => {
    if (!articlePerformance) return [];
    return articlePerformance.trend.map((point) => ({
      date: point.date,
      pageViews: point.page_views,
      likes: point.likes,
      shares: point.shares,
      comments: point.comments,
      conversions: point.conversions,
    }));
  }, [articlePerformance]);

  return (
    <div className="space-y-6">
      {/* ランキングセクション */}
      <Card className="bg-slate-900 border-slate-800 text-slate-100">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>記事ランキング</CardTitle>
              <CardDescription>
                期間: {format(dateRange.start, "yyyy/MM/dd")} -{" "}
                {format(dateRange.end, "yyyy/MM/dd")}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <select
                value={sortBy}
                onChange={(e) =>
                  setSortBy(e.target.value as "page_views" | "engagement" | "conversions")
                }
                className="rounded-md bg-slate-950 border border-slate-800 text-slate-100 px-3 py-2 text-sm"
              >
                <option value="page_views">ページビュー順</option>
                <option value="engagement">エンゲージメント順</option>
                <option value="conversions">コンバージョン順</option>
              </select>
              <button
                onClick={loadRankings}
                disabled={rankingsLoading}
                className="rounded-md bg-slate-100 px-4 py-2 text-slate-900 font-semibold hover:bg-white transition text-sm"
              >
                {rankingsLoading ? "読み込み中..." : "更新"}
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {rankings.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-800">
                    <th className="text-left py-3 px-4 text-slate-400">順位</th>
                    <th className="text-left py-3 px-4 text-slate-400">記事タイトル</th>
                    <th className="text-right py-3 px-4 text-slate-400">PV</th>
                    <th className="text-right py-3 px-4 text-slate-400">UU</th>
                    <th className="text-right py-3 px-4 text-slate-400">いいね</th>
                    <th className="text-right py-3 px-4 text-slate-400">シェア</th>
                    <th className="text-right py-3 px-4 text-slate-400">コメント</th>
                    <th className="text-right py-3 px-4 text-slate-400">エンゲージ率</th>
                    <th className="text-right py-3 px-4 text-slate-400">CV率</th>
                    <th className="text-right py-3 px-4 text-slate-400">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {rankings.map((article, index) => (
                    <tr
                      key={article.article_id}
                      className="border-b border-slate-800 hover:bg-slate-800/50 cursor-pointer"
                      onClick={() => setSelectedArticleId(article.article_id)}
                    >
                      <td className="py-3 px-4">{index + 1}</td>
                      <td className="py-3 px-4">
                        <div className="max-w-md truncate">{article.article_title}</div>
                      </td>
                      <td className="text-right py-3 px-4">
                        {numberFormatter.format(article.metrics.page_views)}
                      </td>
                      <td className="text-right py-3 px-4">
                        {numberFormatter.format(article.metrics.unique_users)}
                      </td>
                      <td className="text-right py-3 px-4">
                        {numberFormatter.format(article.metrics.likes)}
                      </td>
                      <td className="text-right py-3 px-4">
                        {numberFormatter.format(article.metrics.shares)}
                      </td>
                      <td className="text-right py-3 px-4">
                        {numberFormatter.format(article.metrics.comments)}
                      </td>
                      <td className="text-right py-3 px-4">
                        {article.metrics.engagement_rate.toFixed(2)}%
                      </td>
                      <td className="text-right py-3 px-4">
                        {article.metrics.conversion_rate.toFixed(2)}%
                      </td>
                      <td className="text-right py-3 px-4">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedArticleId(article.article_id);
                          }}
                          className="text-blue-400 hover:text-blue-300 text-xs"
                        >
                          詳細
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-slate-400 text-center py-8">
              {rankingsLoading ? "読み込み中..." : "データがありません"}
            </p>
          )}
        </CardContent>
      </Card>

      {/* 記事詳細セクション */}
      {selectedArticleId && (
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>記事詳細分析</CardTitle>
                <CardDescription>
                  {articlePerformance?.article_title || "読み込み中..."}
                </CardDescription>
              </div>
              <button
                onClick={() => {
                  setSelectedArticleId(null);
                  setArticlePerformance(null);
                }}
                className="text-sm text-slate-400 hover:text-slate-300"
              >
                閉じる
              </button>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {detailLoading ? (
              <p className="text-sm text-slate-400 text-center py-8">読み込み中...</p>
            ) : articlePerformance ? (
              <>
                {/* 主要指標 */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <Eye className="h-4 w-4" />
                      <p className="text-xs">ページビュー</p>
                    </div>
                    <p className="text-2xl font-semibold text-white">
                      {numberFormatter.format(articlePerformance.metrics.page_views)}
                    </p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <TrendingUp className="h-4 w-4" />
                      <p className="text-xs">ユニークユーザー</p>
                    </div>
                    <p className="text-2xl font-semibold text-white">
                      {numberFormatter.format(articlePerformance.metrics.unique_users)}
                    </p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <BarChart3 className="h-4 w-4" />
                      <p className="text-xs">平均滞在時間</p>
                    </div>
                    <p className="text-2xl font-semibold text-white">
                      {formatSeconds(articlePerformance.metrics.average_time_on_page)}
                    </p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <Heart className="h-4 w-4" />
                      <p className="text-xs">エンゲージ率</p>
                    </div>
                    <p className="text-2xl font-semibold text-white">
                      {articlePerformance.metrics.engagement_rate.toFixed(2)}%
                    </p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <TrendingUp className="h-4 w-4" />
                      <p className="text-xs">コンバージョン率</p>
                    </div>
                    <p className="text-2xl font-semibold text-white">
                      {articlePerformance.metrics.conversion_rate.toFixed(2)}%
                    </p>
                  </div>
                </div>

                {/* エンゲージメント指標 */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <Heart className="h-4 w-4" />
                      <p className="text-xs">いいね</p>
                    </div>
                    <p className="text-xl font-semibold text-white">
                      {numberFormatter.format(articlePerformance.engagement.likes)}
                    </p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <Share2 className="h-4 w-4" />
                      <p className="text-xs">シェア</p>
                    </div>
                    <p className="text-xl font-semibold text-white">
                      {numberFormatter.format(articlePerformance.engagement.shares)}
                    </p>
                  </div>
                  <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
                    <div className="flex items-center gap-2 text-slate-400 mb-2">
                      <MessageSquare className="h-4 w-4" />
                      <p className="text-xs">コメント</p>
                    </div>
                    <p className="text-xl font-semibold text-white">
                      {numberFormatter.format(articlePerformance.engagement.comments)}
                    </p>
                  </div>
                </div>

                {/* 時系列トレンドチャート */}
                {chartData.length > 0 && (
                  <div className="h-80">
                    <ResponsiveContainerSafe width="100%" height="100%">
                      <LineChartSafe data={chartData}>
                        <CartesianGridSafe strokeDasharray="3 3" stroke="#334155" />
                        <XAxisSafe
                          dataKey="date"
                          tickFormatter={(value: string) => format(new Date(value), "MM/dd")}
                          stroke="#94a3b8"
                        />
                        <YAxisSafe stroke="#94a3b8" />
                        <TooltipSafe
                          contentStyle={{
                            backgroundColor: "#1e293b",
                            border: "1px solid #334155",
                            borderRadius: "8px",
                          }}
                          labelFormatter={(value: string) => format(new Date(value), "yyyy/MM/dd")}
                        />
                        <LegendSafe />
                        <LineSafe
                          type="monotone"
                          dataKey="pageViews"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          dot={false}
                          name="ページビュー"
                        />
                        <LineSafe
                          type="monotone"
                          dataKey="likes"
                          stroke="#ef4444"
                          strokeWidth={2}
                          dot={false}
                          name="いいね"
                        />
                        <LineSafe
                          type="monotone"
                          dataKey="shares"
                          stroke="#10b981"
                          strokeWidth={2}
                          dot={false}
                          name="シェア"
                        />
                        <LineSafe
                          type="monotone"
                          dataKey="comments"
                          stroke="#f59e0b"
                          strokeWidth={2}
                          dot={false}
                          name="コメント"
                        />
                        <LineSafe
                          type="monotone"
                          dataKey="conversions"
                          stroke="#8b5cf6"
                          strokeWidth={2}
                          dot={false}
                          name="コンバージョン"
                        />
                      </LineChartSafe>
                    </ResponsiveContainerSafe>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-slate-400 text-center py-8">データがありません</p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
