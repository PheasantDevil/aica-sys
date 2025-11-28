"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";
import { format } from "date-fns";
import { type ComponentType, useCallback, useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const LineChartSafe = LineChart as unknown as ComponentType<any>;
const LineSafe = Line as unknown as ComponentType<any>;
const BarChartSafe = BarChart as unknown as ComponentType<any>;
const BarSafe = Bar as unknown as ComponentType<any>;
const CartesianGridSafe = CartesianGrid as unknown as ComponentType<any>;
const XAxisSafe = XAxis as unknown as ComponentType<any>;
const YAxisSafe = YAxis as unknown as ComponentType<any>;
const TooltipSafe = Tooltip as unknown as ComponentType<any>;
const LegendSafe = Legend as unknown as ComponentType<any>;
const ResponsiveContainerSafe = ResponsiveContainer as unknown as ComponentType<any>;

const currencyFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0,
});

const percentFormatter = new Intl.NumberFormat("ja-JP", {
  maximumFractionDigits: 2,
});

const RANGE_OPTIONS = [
  { label: "過去30日", value: 30 },
  { label: "過去90日", value: 90 },
  { label: "過去180日", value: 180 },
];

interface BusinessInsights {
  period: { start: string; end: string };
  revenue: {
    summary: Record<string, any>;
    mrr_trend: Array<{ period: string; mrr: number }>;
    plan_breakdown: Array<{ plan: string; mrr: number }>;
  };
  user_growth: Record<string, any>;
  behavior: Record<string, any>;
  content: Record<string, any>;
  top_articles: Array<Record<string, any>>;
  alerts: string[];
}

export function AdminBusinessInsights() {
  const [range, setRange] = useState(90);
  const [insights, setInsights] = useState<BusinessInsights | null>(null);
  const { loading, execute } = useApiCall<{ success: boolean; insights: BusinessInsights }>();

  const fetchInsights = useCallback(async () => {
    const end = new Date();
    const start = new Date(end);
    start.setDate(end.getDate() - range);

    const response = await execute(() =>
      apiClient.getBusinessInsights({
        startDate: start.toISOString(),
        endDate: end.toISOString(),
      }),
    );

    if (response?.success) {
      setInsights(response.insights);
    }
  }, [range, execute]);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const revenueSummary = insights?.revenue?.summary ?? {};

  const mrrTrendData = useMemo(() => {
    return (insights?.revenue?.mrr_trend ?? []).map((point) => ({
      period: point.period,
      label: format(new Date(point.period), "yyyy/MM"),
      mrr: point.mrr,
    }));
  }, [insights]);

  const behaviorTrend = useMemo(() => {
    const trend = insights?.behavior?.trend ?? [];
    return trend.map((point: any) => ({
      date: point.date,
      label: format(new Date(point.date), "MM/dd"),
      pageViews: point.page_views,
      conversions: point.conversions,
    }));
  }, [insights]);

  const planBreakdown = useMemo(() => {
    const breakdown = insights?.revenue?.plan_breakdown ?? [];
    const total = breakdown.reduce((sum: number, item: any) => sum + item.mrr, 0);
    return breakdown.map((item: any) => ({
      plan: item.plan,
      mrr: item.mrr,
      ratio: total ? Math.round((item.mrr / total) * 100) : 0,
    }));
  }, [insights]);

  const dateLabel = insights
    ? `${format(new Date(insights.period.start), "yyyy/MM/dd")} - ${format(
        new Date(insights.period.end),
        "yyyy/MM/dd",
      )}`
    : "-";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm text-slate-400">BUSINESS INSIGHTS</p>
          <h1 className="text-2xl font-semibold text-white mt-1">
            ビジネスインサイトダッシュボード
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            収益・ユーザー・コンテンツのKPIを横断的に可視化します。
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-400">期間:</label>
          <select
            value={range}
            onChange={(event) => setRange(Number(event.target.value))}
            className="rounded-md bg-slate-950 border border-slate-800 text-slate-100 px-3 py-2 text-sm"
          >
            {RANGE_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <button
            onClick={fetchInsights}
            className="rounded-md bg-slate-100 px-4 py-2 text-slate-900 text-sm font-semibold hover:bg-white transition"
            disabled={loading}
          >
            {loading ? "更新中..." : "再取得"}
          </button>
        </div>
      </div>

      <Card className="bg-slate-900 border-slate-800 text-slate-100">
        <CardHeader>
          <CardTitle>主要指標</CardTitle>
          <CardDescription>期間: {dateLabel}</CardDescription>
        </CardHeader>
        <CardContent>
          {loading && !insights ? (
            <div className="flex items-center justify-center py-10">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-4">
              <MetricStat label="MRR" value={currencyFormatter.format(revenueSummary.mrr ?? 0)} />
              <MetricStat
                label="ARR"
                value={currencyFormatter.format(revenueSummary.arr ?? 0)}
                description={`前期比 ${percentFormatter.format(
                  revenueSummary.arr_growth_rate ?? 0,
                )}%`}
              />
              <MetricStat
                label="新規ユーザー"
                value={`${insights?.user_growth?.new_users ?? 0} 人`}
                description={`純増 ${insights?.user_growth?.net_growth ?? 0} 人`}
              />
              <MetricStat
                label="コンバージョン率"
                value={`${percentFormatter.format(
                  insights?.behavior?.overview?.conversion_rate ?? 0,
                )}%`}
                description={`${
                  insights?.behavior?.conversion_metrics?.total_conversions ?? 0
                } 回のCV`}
              />
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>MRR 推移</CardTitle>
            <CardDescription>月次経常収益のトレンド</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            {loading && !insights ? (
              <div className="flex h-full items-center justify-center">
                <LoadingSpinner />
              </div>
            ) : mrrTrendData.length ? (
              <ResponsiveContainerSafe width="100%" height="100%">
                <LineChartSafe data={mrrTrendData}>
                  <CartesianGridSafe strokeDasharray="3 3" stroke="#334155" />
                  <XAxisSafe dataKey="label" stroke="#94a3b8" />
                  <YAxisSafe stroke="#94a3b8" />
                  <TooltipSafe
                    contentStyle={{
                      backgroundColor: "#1e293b",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                    }}
                    formatter={(value: number) => currencyFormatter.format(value)}
                  />
                  <LineSafe
                    type="monotone"
                    dataKey="mrr"
                    stroke="#22d3ee"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChartSafe>
              </ResponsiveContainerSafe>
            ) : (
              <EmptyState message="データがありません" />
            )}
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>ユーザー行動トレンド</CardTitle>
            <CardDescription>PVとコンバージョンの推移</CardDescription>
          </CardHeader>
          <CardContent className="h-80">
            {behaviorTrend.length ? (
              <ResponsiveContainerSafe width="100%" height="100%">
                <LineChartSafe data={behaviorTrend}>
                  <CartesianGridSafe strokeDasharray="3 3" stroke="#334155" />
                  <XAxisSafe dataKey="label" stroke="#94a3b8" />
                  <YAxisSafe stroke="#94a3b8" />
                  <TooltipSafe
                    contentStyle={{
                      backgroundColor: "#1e293b",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                    }}
                  />
                  <LegendSafe />
                  <LineSafe
                    type="monotone"
                    dataKey="pageViews"
                    stroke="#38bdf8"
                    strokeWidth={2}
                    dot={false}
                    name="PV"
                  />
                  <LineSafe
                    type="monotone"
                    dataKey="conversions"
                    stroke="#a78bfa"
                    strokeWidth={2}
                    dot={false}
                    name="コンバージョン"
                  />
                </LineChartSafe>
              </ResponsiveContainerSafe>
            ) : (
              <EmptyState message="データがありません" />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>プラン別 MRR</CardTitle>
            <CardDescription>プラン毎の月次売上構成比</CardDescription>
          </CardHeader>
          <CardContent>
            {planBreakdown.length ? (
              planBreakdown.map((item) => (
                <div key={item.plan} className="mb-4 last:mb-0">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-300">{item.plan}</span>
                    <span className="text-slate-400">
                      {currencyFormatter.format(item.mrr)} ・ {item.ratio}%
                    </span>
                  </div>
                  <div className="mt-2 h-2 w-full rounded-full bg-slate-800">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
                      style={{ width: `${item.ratio}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <EmptyState message="プラン別データがありません" />
            )}
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>行動指標</CardTitle>
            <CardDescription>セッション/エンゲージメントの要約</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <MetricStat
              label="平均滞在時間"
              value={`${Math.round(
                insights?.behavior?.session_metrics?.average_session_duration ?? 0,
              )} 秒`}
            />
            <MetricStat
              label="直帰率"
              value={`${percentFormatter.format(
                insights?.behavior?.session_metrics?.bounce_rate ?? 0,
              )}%`}
            />
            <MetricStat
              label="平均スクロール率"
              value={`${percentFormatter.format(
                insights?.behavior?.page_metrics?.average_scroll_depth ?? 0,
              )}%`}
            />
            <MetricStat
              label="総ページビュー"
              value={`${insights?.behavior?.overview?.total_page_views ?? 0} 回`}
            />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>トップ記事</CardTitle>
            <CardDescription>パフォーマンス上位の記事</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {insights?.top_articles?.length ? (
              insights.top_articles.map((article: any, index: number) => (
                <div
                  key={article.article_id ?? index}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm"
                >
                  <div className="max-w-[70%]">
                    <p className="text-slate-100 truncate">{article.article_title ?? "Untitled"}</p>
                    <p className="text-xs text-slate-400">PV {article.metrics?.page_views ?? 0}</p>
                  </div>
                  <div className="text-right text-xs text-slate-400">
                    CV {article.metrics?.conversions ?? 0}
                    <br />
                    ER {percentFormatter.format(article.metrics?.engagement_rate ?? 0)}%
                  </div>
                </div>
              ))
            ) : (
              <EmptyState message="記事データがありません" />
            )}
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>アラート</CardTitle>
            <CardDescription>改善が必要な指標を自動検知</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {insights?.alerts?.length ? (
              insights.alerts.map((alert, index) => (
                <div
                  key={`${alert}-${index}`}
                  className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-sm"
                >
                  {alert}
                </div>
              ))
            ) : (
              <EmptyState message="特筆すべきアラートはありません" />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

interface MetricStatProps {
  label: string;
  value: string;
  description?: string;
}

function MetricStat({ label, value, description }: MetricStatProps) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-2xl font-semibold text-white mt-1">{value}</p>
      {description ? <p className="text-xs text-slate-400 mt-1">{description}</p> : null}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center text-sm text-slate-400">{message}</div>
  );
}
