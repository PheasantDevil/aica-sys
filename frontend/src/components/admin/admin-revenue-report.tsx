"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";
import { format } from "date-fns";
import { type ComponentType, useCallback, useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const LineChartSafe = LineChart as unknown as ComponentType<any>;
const LineSafe = Line as unknown as ComponentType<any>;
const CartesianGridSafe = CartesianGrid as unknown as ComponentType<any>;
const XAxisSafe = XAxis as unknown as ComponentType<any>;
const YAxisSafe = YAxis as unknown as ComponentType<any>;
const TooltipSafe = Tooltip as unknown as ComponentType<any>;
const ResponsiveContainerSafe = ResponsiveContainer as unknown as ComponentType<any>;

type RevenueReport = {
  period: { start: string; end: string };
  summary: {
    total_revenue: number;
    mrr: number;
    arr: number;
    arr_growth_rate: number;
    active_customers: number;
    invoice_count: number;
    average_order_value: number;
  };
  plan_breakdown: Array<{ plan: string; mrr: number }>;
  mrr_trend: Array<{ period: string; mrr: number }>;
  ltv: {
    ltv: number;
    average_revenue_per_user: number;
    churn_rate: number;
  };
  acquisition: {
    new_customers: number;
    marketing_spend: number;
    cac: number;
    ltv_to_cac?: number | null;
  };
  alerts: string[];
};

const currencyFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 0,
});

const decimalCurrencyFormatter = new Intl.NumberFormat("ja-JP", {
  style: "currency",
  currency: "JPY",
  maximumFractionDigits: 2,
});

const percentFormatter = new Intl.NumberFormat("ja-JP", {
  maximumFractionDigits: 2,
});

const RANGE_OPTIONS = [
  { label: "過去30日", value: 30 },
  { label: "過去90日", value: 90 },
  { label: "過去180日", value: 180 },
];

export function AdminRevenueReport() {
  const [range, setRange] = useState<number>(90);
  const [report, setReport] = useState<RevenueReport | null>(null);
  const { loading, execute } = useApiCall<{ success: boolean; report: RevenueReport }>();

  const fetchReport = useCallback(async () => {
    const end = new Date();
    const start = new Date(end);
    start.setDate(end.getDate() - range);

    const response = await execute(() =>
      apiClient.getRevenueReport({
        startDate: start.toISOString(),
        endDate: end.toISOString(),
      }),
    );

    if (response?.success) {
      setReport(response.report);
    }
  }, [range, execute]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const planTotals = useMemo(() => {
    if (!report)
      return { total: 0, items: [] as Array<{ plan: string; mrr: number; ratio: number }> };
    const total = report.plan_breakdown.reduce((sum, item) => sum + item.mrr, 0);
    const items = report.plan_breakdown.map((item) => ({
      plan: item.plan,
      mrr: item.mrr,
      ratio: total ? Math.round((item.mrr / total) * 100) : 0,
    }));
    return { total, items };
  }, [report]);

  const mrrTrendData = useMemo(() => {
    if (!report) return [];
    return report.mrr_trend.map((point) => ({
      period: point.period,
      label: format(new Date(point.period), "yyyy/MM"),
      mrr: point.mrr,
    }));
  }, [report]);

  const dateLabel =
    report && report.period
      ? `${format(new Date(report.period.start), "yyyy/MM/dd")} - ${format(
          new Date(report.period.end),
          "yyyy/MM/dd",
        )}`
      : "-";

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm text-slate-400">REVENUE REPORT</p>
          <h1 className="text-2xl font-semibold text-white mt-1">収益レポート</h1>
          <p className="text-sm text-slate-400 mt-2">
            MRR/ARR/LTV/CAC を含む収益指標を可視化します。
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
            onClick={fetchReport}
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
          {loading && !report ? (
            <div className="flex items-center justify-center py-10">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-4">
              <MetricStat label="MRR" value={currencyFormatter.format(report?.summary.mrr ?? 0)} />
              <MetricStat
                label="ARR"
                value={currencyFormatter.format(report?.summary.arr ?? 0)}
                description={`前期比 ${percentFormatter.format(
                  report?.summary.arr_growth_rate ?? 0,
                )}%`}
              />
              <MetricStat
                label="総収益"
                value={currencyFormatter.format(report?.summary.total_revenue ?? 0)}
              />
              <MetricStat
                label="平均受注額"
                value={decimalCurrencyFormatter.format(report?.summary.average_order_value ?? 0)}
                description={`${report?.summary.invoice_count ?? 0} 件の支払い`}
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
            {loading && !report ? (
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
              <div className="flex h-full items-center justify-center text-sm text-slate-400">
                データがありません
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>LTV / CAC</CardTitle>
            <CardDescription>顧客ライフタイム価値と獲得コスト</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <MetricStat
                label="LTV"
                value={currencyFormatter.format(report?.ltv.ltv ?? 0)}
                description={`ARPU ${decimalCurrencyFormatter.format(
                  report?.ltv.average_revenue_per_user ?? 0,
                )}`}
              />
              <MetricStat
                label="チャーン率"
                value={`${percentFormatter.format(report?.ltv.churn_rate ?? 0)}%`}
                description="期間内の解約率"
              />
              <MetricStat
                label="CAC"
                value={currencyFormatter.format(report?.acquisition.cac ?? 0)}
                description={`新規顧客 ${report?.acquisition.new_customers ?? 0} 名`}
              />
              <MetricStat
                label="LTV/CAC"
                value={
                  report?.acquisition.ltv_to_cac
                    ? percentFormatter.format(report.acquisition.ltv_to_cac)
                    : "-"
                }
                description="3x 以上が理想"
              />
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">
              <p className="text-sm text-slate-400">マーケティング費用</p>
              <p className="text-2xl font-semibold text-white mt-1">
                {currencyFormatter.format(report?.acquisition.marketing_spend ?? 0)}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>プラン別 MRR</CardTitle>
            <CardDescription>プラン毎の月次収益内訳</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {planTotals.items.length ? (
              planTotals.items.map((item) => (
                <div key={item.plan}>
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
              <p className="text-sm text-slate-400">プラン別データがありません。</p>
            )}
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800 text-slate-100">
          <CardHeader>
            <CardTitle>アラート</CardTitle>
            <CardDescription>改善が必要な指標を自動検出</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {report?.alerts?.length ? (
              report.alerts.map((alert, index) => (
                <div
                  key={`${alert}-${index}`}
                  className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-sm"
                >
                  {alert}
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400">特筆すべきアラートはありません。</p>
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
