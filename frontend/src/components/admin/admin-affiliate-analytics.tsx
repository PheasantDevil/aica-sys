"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";
import { useEffect, useState } from "react";

interface ClickStats {
  total_clicks: number;
  unique_sessions: number;
  unique_referrers: number;
}

export function AdminAffiliateAnalytics() {
  const [stats, setStats] = useState<ClickStats | null>(null);
  const [affiliateId, setAffiliateId] = useState<string>("");
  const [linkId, setLinkId] = useState<string>("");
  const { loading, execute } = useApiCall<{ statistics: ClickStats }>();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    const response = await execute(() =>
      apiClient.getClickStatistics({
        affiliate_id: affiliateId ? Number(affiliateId) : undefined,
        link_id: linkId ? Number(linkId) : undefined,
      }),
    );
    if (response?.statistics) {
      setStats(response.statistics);
    }
  };

  const StatCard = ({ label, value }: { label: string; value: number | string }) => (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-3xl font-semibold text-white mt-2">{value}</p>
    </div>
  );

  return (
    <Card className="bg-slate-900 border-slate-800 text-slate-100">
      <CardContent className="pt-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-slate-400 mb-1">パートナーIDでフィルタ</p>
            <Input
              placeholder="例: 12"
              value={affiliateId}
              onChange={(event) => setAffiliateId(event.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100"
            />
          </div>
          <div>
            <p className="text-xs text-slate-400 mb-1">リンクIDでフィルタ</p>
            <Input
              placeholder="例: 102"
              value={linkId}
              onChange={(event) => setLinkId(event.target.value)}
              className="bg-slate-950 border-slate-800 text-slate-100"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={loadStats}
              className="w-full rounded-md bg-slate-100 py-2 text-slate-900 font-semibold hover:bg-white transition"
              disabled={loading}
            >
              {loading ? "読み込み中..." : "統計を更新"}
            </button>
          </div>
        </div>

        {stats ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard label="総クリック数" value={stats.total_clicks} />
            <StatCard label="ユニークセッション" value={stats.unique_sessions} />
            <StatCard label="ユニークリファラー" value={stats.unique_referrers} />
          </div>
        ) : (
          <p className="text-sm text-slate-400">統計データを読み込んでください。</p>
        )}
      </CardContent>
    </Card>
  );
}
