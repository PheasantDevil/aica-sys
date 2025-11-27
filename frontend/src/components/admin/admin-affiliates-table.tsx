"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";
import { Crown } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

interface AffiliateSummary {
  id: number;
  user_id: string;
  affiliate_code: string;
  tier: string;
  total_clicks: number;
  total_conversions: number;
  total_revenue: number;
  total_commission: number;
  status: string;
  balance: number;
}

export function AdminAffiliatesTable() {
  const [affiliates, setAffiliates] = useState<AffiliateSummary[]>([]);
  const [search, setSearch] = useState("");
  const { loading, execute } = useApiCall<{ affiliates: AffiliateSummary[]; count: number }>();

  const loadAffiliates = useCallback(async () => {
    const response = await execute(() => apiClient.getTopAffiliates(50, "total_revenue"));
    if (response?.affiliates) {
      setAffiliates(response.affiliates);
    } else if (!response) {
      toast.error("パートナー情報の取得に失敗しました");
    }
  }, [execute]);

  useEffect(() => {
    loadAffiliates();
  }, [loadAffiliates]);

  const filtered = useMemo(() => {
    if (!search) return affiliates;
    const term = search.toLowerCase();
    return affiliates.filter(
      (affiliate) =>
        affiliate.affiliate_code.toLowerCase().includes(term) ||
        affiliate.tier.toLowerCase().includes(term),
    );
  }, [affiliates, search]);

  return (
    <Card className="bg-slate-900 border-slate-800 text-slate-100">
      <CardContent className="pt-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <Input
            placeholder="コードまたはティアで検索"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="bg-slate-950 border-slate-800 focus-visible:ring-slate-500"
          />
          <div className="flex items-center gap-2">
            <Button variant="outline" className="border-slate-700" onClick={loadAffiliates}>
              更新
            </Button>
          </div>
        </div>

        <div className="overflow-x-auto rounded border border-slate-800">
          <table className="min-w-full divide-y divide-slate-800 text-sm">
            <thead className="bg-slate-900/60">
              <tr className="text-slate-400">
                <th className="px-4 py-3 text-left font-medium">コード</th>
                <th className="px-4 py-3 text-left font-medium">ティア</th>
                <th className="px-4 py-3 text-right font-medium">クリック</th>
                <th className="px-4 py-3 text-right font-medium">コンバージョン</th>
                <th className="px-4 py-3 text-right font-medium">総収益</th>
                <th className="px-4 py-3 text-right font-medium">総コミッション</th>
                <th className="px-4 py-3 text-right font-medium">残高</th>
                <th className="px-4 py-3 text-left font-medium">ステータス</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filtered.map((affiliate) => (
                <tr key={affiliate.id} className="hover:bg-slate-900/40">
                  <td className="px-4 py-3 font-mono text-xs text-slate-300">
                    {affiliate.affiliate_code}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 rounded-full bg-slate-800 px-2 py-1 text-xs font-medium text-slate-200">
                      {affiliate.tier}
                      {affiliate.tier === "platinum" && (
                        <Crown className="h-3 w-3 text-yellow-400" />
                      )}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">{affiliate.total_clicks}</td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {affiliate.total_conversions}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    ¥{affiliate.total_revenue.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    ¥{affiliate.total_commission.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    ¥{affiliate.balance.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-left">
                    <span
                      className={
                        affiliate.status === "active"
                          ? "text-emerald-400 text-xs"
                          : "text-slate-400 text-xs"
                      }
                    >
                      {affiliate.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {loading && <p className="text-xs text-slate-400">読み込み中...</p>}
        {!loading && filtered.length === 0 && (
          <p className="text-xs text-slate-400">該当するパートナーが見つかりませんでした。</p>
        )}
      </CardContent>
    </Card>
  );
}
