"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { apiClient } from "@/lib/api-client";
import { useApiCall } from "@/hooks/use-api";
import { Copy, ExternalLink, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface ReferralLink {
  id: number;
  link_code: string;
  campaign_name: string | null;
  destination_url: string;
  clicks: number;
  conversions: number;
  is_active: boolean;
  valid_until: string | null;
  created_at: string;
}

interface ReferralLinkManagerProps {
  affiliateId: number;
}

export function ReferralLinkManager({ affiliateId }: ReferralLinkManagerProps) {
  const [links, setLinks] = useState<ReferralLink[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeOnly, setActiveOnly] = useState(true);
  const [formData, setFormData] = useState({
    destination_url: "",
    campaign_name: "",
    valid_until: "",
  });

  const { loading, execute } = useApiCall<{ links: ReferralLink[]; count: number }>();
  const { loading: creating, execute: createLink } = useApiCall<{ link: ReferralLink }>();

  useEffect(() => {
    loadLinks();
  }, [affiliateId, activeOnly]);

  const loadLinks = async () => {
    const result = await execute(() => apiClient.getReferralLinks(affiliateId, activeOnly));
    if (result) {
      setLinks(result.links || []);
    }
  };

  const handleCreateLink = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.destination_url) {
      toast.error("送信先URLを入力してください");
      return;
    }

    const result = await createLink(() =>
      apiClient.createReferralLink({
        affiliate_id: affiliateId,
        destination_url: formData.destination_url,
        campaign_name: formData.campaign_name || undefined,
        valid_until: formData.valid_until || undefined,
      }),
    );

    if (result) {
      toast.success("紹介リンクを作成しました");
      setFormData({ destination_url: "", campaign_name: "", valid_until: "" });
      setShowCreateForm(false);
      loadLinks();
    }
  };

  const copyToClipboard = (linkCode: string) => {
    const baseUrl = window.location.origin;
    const fullLink = `${baseUrl}/ref/${linkCode}`;
    navigator.clipboard.writeText(fullLink);
    toast.success("リンクをクリップボードにコピーしました");
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "無期限";
    return new Date(dateString).toLocaleDateString("ja-JP");
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>紹介リンク管理</CardTitle>
            <CardDescription>紹介リンクの生成、管理、統計の確認ができます</CardDescription>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Switch id="active-only" checked={activeOnly} onCheckedChange={setActiveOnly} />
              <Label htmlFor="active-only" className="text-sm">
                アクティブのみ
              </Label>
            </div>
            <Button onClick={() => setShowCreateForm(!showCreateForm)} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              リンク作成
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {showCreateForm && (
          <Card className="bg-gray-50">
            <CardContent className="pt-6">
              <form onSubmit={handleCreateLink} className="space-y-4">
                <div>
                  <Label htmlFor="destination_url">送信先URL *</Label>
                  <Input
                    id="destination_url"
                    type="url"
                    value={formData.destination_url}
                    onChange={(e) => setFormData({ ...formData, destination_url: e.target.value })}
                    placeholder="https://example.com"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="campaign_name">キャンペーン名（任意）</Label>
                  <Input
                    id="campaign_name"
                    type="text"
                    value={formData.campaign_name}
                    onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })}
                    placeholder="例: 2024年新春キャンペーン"
                  />
                </div>
                <div>
                  <Label htmlFor="valid_until">有効期限（任意）</Label>
                  <Input
                    id="valid_until"
                    type="datetime-local"
                    value={formData.valid_until}
                    onChange={(e) => setFormData({ ...formData, valid_until: e.target.value })}
                  />
                </div>
                <div className="flex space-x-2">
                  <Button type="submit" disabled={creating}>
                    {creating ? "作成中..." : "リンクを作成"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowCreateForm(false);
                      setFormData({ destination_url: "", campaign_name: "", valid_until: "" });
                    }}
                  >
                    キャンセル
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {loading ? (
          <div className="text-center py-8 text-gray-600">読み込み中...</div>
        ) : links.length === 0 ? (
          <div className="text-center py-8 text-gray-600">
            紹介リンクがありません。リンクを作成してください。
          </div>
        ) : (
          <div className="space-y-4">
            {links.map((link) => {
              const fullLink = `${window.location.origin}/ref/${link.link_code}`;
              return (
                <Card key={link.id} className="bg-white">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold">
                            {link.campaign_name || "無題のキャンペーン"}
                          </h3>
                          <span
                            className={`text-xs px-2 py-1 rounded ${
                              link.is_active
                                ? "bg-green-100 text-green-800"
                                : "bg-gray-100 text-gray-800"
                            }`}
                          >
                            {link.is_active ? "アクティブ" : "非アクティブ"}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 space-y-1">
                          <div>
                            <span className="font-medium">リンクコード:</span>{" "}
                            <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                              {link.link_code}
                            </code>
                          </div>
                          <div>
                            <span className="font-medium">送信先:</span>{" "}
                            <a
                              href={link.destination_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline flex items-center space-x-1"
                            >
                              <span>{link.destination_url}</span>
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          </div>
                          <div className="flex items-center space-x-4 text-xs">
                            <span>
                              <span className="font-medium">クリック:</span> {link.clicks}
                            </span>
                            <span>
                              <span className="font-medium">コンバージョン:</span>{" "}
                              {link.conversions}
                            </span>
                            <span>
                              <span className="font-medium">有効期限:</span>{" "}
                              {formatDate(link.valid_until)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 ml-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(link.link_code)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
