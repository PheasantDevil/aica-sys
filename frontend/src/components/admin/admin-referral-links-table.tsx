"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useApiCall } from "@/hooks/use-api";
import { apiClient } from "@/lib/api-client";
import { format } from "date-fns";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

interface AdminReferralLink {
  id: number;
  affiliate_id: number;
  link_code: string;
  destination_url: string;
  campaign_name?: string | null;
  clicks: number;
  conversions: number;
  is_active: boolean;
  valid_until?: string | null;
  created_at?: string;
}

export function AdminReferralLinksTable() {
  const [links, setLinks] = useState<AdminReferralLink[]>([]);
  const [search, setSearch] = useState("");
  const [activeOnly, setActiveOnly] = useState(true);
  const { loading, execute } = useApiCall<{ links: AdminReferralLink[]; count: number }>();
  const { execute: updateLink } = useApiCall<{ link: AdminReferralLink }>();

  useEffect(() => {
    loadLinks();
  }, [activeOnly]);

  const loadLinks = async () => {
    const response = await execute(() =>
      apiClient.getAllReferralLinks(activeOnly, activeOnly ? 200 : 100),
    );
    if (response?.links) {
      setLinks(response.links);
    }
  };

  const filtered = useMemo(() => {
    if (!search) return links;
    const term = search.toLowerCase();
    return links.filter(
      (link) =>
        link.link_code.toLowerCase().includes(term) ||
        (link.campaign_name || "").toLowerCase().includes(term) ||
        link.destination_url.toLowerCase().includes(term),
    );
  }, [links, search]);

  const handleToggleActive = async (link: AdminReferralLink) => {
    const newValue = !link.is_active;
    const response = await updateLink(() =>
      apiClient.updateReferralLink(link.id, { is_active: newValue }),
    );
    if (response?.link) {
      toast.success(`リンクを${newValue ? "有効化" : "無効化"}しました`);
      setLinks((prev) =>
        prev.map((item) => (item.id === link.id ? { ...item, is_active: newValue } : item)),
      );
    } else {
      toast.error("更新に失敗しました");
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800 text-slate-100">
      <CardContent className="pt-6 space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <Input
            placeholder="リンクコード / URL / キャンペーン名で検索"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="bg-slate-950 border-slate-800 focus-visible:ring-slate-500"
          />
          <div className="flex items-center gap-3 text-sm">
            <span className="text-slate-400">アクティブのみ</span>
            <Switch checked={activeOnly} onCheckedChange={setActiveOnly} />
            <Button variant="outline" className="border-slate-700" onClick={loadLinks}>
              更新
            </Button>
          </div>
        </div>

        <div className="overflow-auto rounded border border-slate-800">
          <table className="min-w-full divide-y divide-slate-800 text-sm">
            <thead className="bg-slate-900/60 text-slate-400">
              <tr>
                <th className="px-4 py-2 text-left">コード</th>
                <th className="px-4 py-2 text-left">キャンペーン</th>
                <th className="px-4 py-2 text-left">送信先</th>
                <th className="px-4 py-2 text-right">クリック</th>
                <th className="px-4 py-2 text-right">CV</th>
                <th className="px-4 py-2 text-left">有効期限</th>
                <th className="px-4 py-2 text-center">アクティブ</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filtered.map((link) => (
                <tr key={link.id} className="hover:bg-slate-900/40">
                  <td className="px-4 py-2 font-mono text-xs">{link.link_code}</td>
                  <td className="px-4 py-2">
                    {link.campaign_name || <span className="text-slate-500">（未設定）</span>}
                  </td>
                  <td className="px-4 py-2 max-w-xs truncate">
                    <a
                      href={link.destination_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-300 hover:underline text-xs"
                    >
                      {link.destination_url}
                    </a>
                  </td>
                  <td className="px-4 py-2 text-right tabular-nums">{link.clicks}</td>
                  <td className="px-4 py-2 text-right tabular-nums">{link.conversions}</td>
                  <td className="px-4 py-2 text-left text-xs text-slate-300">
                    {link.valid_until
                      ? format(new Date(link.valid_until), "yyyy/MM/dd HH:mm")
                      : "無期限"}
                  </td>
                  <td className="px-4 py-2 text-center">
                    <Switch
                      checked={link.is_active}
                      onCheckedChange={() => handleToggleActive(link)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {loading && <p className="text-xs text-slate-400">読み込み中...</p>}
      </CardContent>
    </Card>
  );
}
