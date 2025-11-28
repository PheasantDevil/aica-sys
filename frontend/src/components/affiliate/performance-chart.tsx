"use client";

import { format } from "date-fns";
import { TrendingUp } from "lucide-react";
import { type ComponentType, useEffect, useMemo, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";

interface PerformanceChartProps {
  affiliateId: number;
}

interface TrendPoint {
  date: string;
  page_views: number;
  conversions: number;
  avg_scroll_depth: number;
}

interface UserBehaviorAnalytics {
  period: {
    start: string;
    end: string;
  };
  overview: {
    total_page_views: number;
    unique_users: number;
    total_sessions: number;
    conversion_rate: number;
  };
  page_metrics: {
    average_time_on_page: number;
    average_scroll_depth: number;
  };
  session_metrics: {
    average_session_duration: number;
    bounce_rate: number;
  };
  conversion_metrics: {
    total_conversions: number;
    conversion_value: number;
  };
  engagement: {
    scroll_distribution: Record<string, number>;
  };
  trend: TrendPoint[];
}

const numberFormatter = new Intl.NumberFormat("ja-JP");
const LineChartSafe = LineChart as unknown as ComponentType<any>;
const LineSafe = Line as unknown as ComponentType<any>;
const CartesianGridSafe = CartesianGrid as unknown as ComponentType<any>;
const XAxisSafe = XAxis as unknown as ComponentType<any>;
const YAxisSafe = YAxis as unknown as ComponentType<any>;
const TooltipSafe = Tooltip as unknown as ComponentType<any>;
const LegendSafe = Legend as unknown as ComponentType<any>;

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

function MetricStat({
  label,
  value,
  description,
}: {
  label: string;
  value: string;
  description?: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      {description ? <p className="text-xs text-muted-foreground">{description}</p> : null}
    </div>
  );
}

export function PerformanceChart({ affiliateId }: PerformanceChartProps) {
  const [analytics, setAnalytics] = useState<UserBehaviorAnalytics | null>(null);
  const { loading, execute } = useApiCall<{ success: boolean; analytics: UserBehaviorAnalytics }>();

  useEffect(() => {
    const fetchAnalytics = async () => {
      const end = new Date();
      const start = new Date(end.getTime() - 13 * 24 * 60 * 60 * 1000);

      const result = await execute(() =>
        apiClient.getUserBehaviorAnalytics({
          startDate: start.toISOString(),
          endDate: end.toISOString(),
          affiliateId,
        }),
      );

      if (result?.success) {
        setAnalytics(result.analytics);
      }
    };

    fetchAnalytics();
  }, [affiliateId, execute]);

  const chartData = useMemo(() => {
    if (!analytics) return [];
    return analytics.trend.map((point) => ({
      date: point.date,
      pageViews: point.page_views,
      conversions: point.conversions,
    }));
  }, [analytics]);

  const chartWidth = useMemo(() => {
    const points = chartData.length || 1;
    return Math.max(points * 60, 600);
  }, [chartData.length]);

  const scrollDistribution = useMemo(() => {
    if (!analytics) return [];
    const entries = Object.entries(analytics.engagement.scroll_distribution);
    const total = entries.reduce((sum, [, value]) => sum + value, 0);
    return entries.map(([range, count]) => ({
      range,
      ratio: total ? Math.round((count / total) * 100) : 0,
      count,
    }));
  }, [analytics]);

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>パフォーマンス分析</CardTitle>
            <CardDescription>ユーザー行動とコンバージョンのトレンド</CardDescription>
          </div>
          <TrendingUp className="h-5 w-5 text-gray-400" />
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-4">
          <MetricStat
            label="総ページビュー"
            value={numberFormatter.format(analytics?.overview?.total_page_views ?? 0)}
          />
          <MetricStat
            label="ユニーク訪問者"
            value={numberFormatter.format(analytics?.overview?.unique_users ?? 0)}
          />
          <MetricStat
            label="平均滞在時間"
            value={formatSeconds(analytics?.page_metrics?.average_time_on_page ?? 0)}
          />
          <MetricStat
            label="コンバージョン率"
            value={`${(analytics?.overview?.conversion_rate ?? 0).toFixed(2)}%`}
          />
        </div>

        <div className="h-72">
          {loading ? (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              データを読み込み中...
            </div>
          ) : chartData.length ? (
            <div className="h-full w-full overflow-x-auto">
              <LineChartSafe data={chartData} width={chartWidth} height={260}>
                <CartesianGridSafe strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxisSafe
                  dataKey="date"
                  tickFormatter={(value: string) => format(new Date(value), "MM/dd")}
                  stroke="#9ca3af"
                />
                <YAxisSafe stroke="#9ca3af" />
                <TooltipSafe
                  contentStyle={{ fontSize: "12px" }}
                  labelFormatter={(value: string) => format(new Date(value), "yyyy/MM/dd")}
                />
                <LegendSafe />
                <LineSafe
                  type="monotone"
                  dataKey="pageViews"
                  stroke="#2563eb"
                  strokeWidth={2}
                  dot={false}
                  name="ページビュー"
                />
                <LineSafe
                  type="monotone"
                  dataKey="conversions"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                  name="コンバージョン"
                />
              </LineChartSafe>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
              集計期間内のデータがありません
            </div>
          )}
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <MetricStat
            label="平均スクロール率"
            value={`${(analytics?.page_metrics?.average_scroll_depth ?? 0).toFixed(1)}%`}
            description="閲覧ページにおける平均スクロール深度"
          />
          <MetricStat
            label="平均セッション時間"
            value={formatSeconds(analytics?.session_metrics?.average_session_duration ?? 0)}
            description="訪問開始から離脱までの平均時間"
          />
          <MetricStat
            label="直帰率"
            value={`${(analytics?.session_metrics?.bounce_rate ?? 0).toFixed(1)}%`}
            description="1PV以下で離脱したセッション割合"
          />
        </div>

        <div>
          <p className="mb-2 text-sm font-semibold">スクロール深度の分布</p>
          <div className="grid gap-3 md:grid-cols-4">
            {scrollDistribution.map((item) => (
              <div key={item.range} className="rounded-lg border p-3">
                <p className="text-xs text-muted-foreground">{item.range}</p>
                <p className="text-lg font-semibold">{item.ratio}%</p>
                <p className="text-xs text-muted-foreground">{item.count} セッション</p>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
