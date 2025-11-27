"use client";

import { AffiliateStatsCards } from "@/components/affiliate/affiliate-stats-cards";
import { CommissionHistory } from "@/components/affiliate/commission-history";
import { PerformanceChart } from "@/components/affiliate/performance-chart";
import { ReferralLinkManager } from "@/components/affiliate/referral-link-manager";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import { useApiCall } from "@/hooks/use-api";
import { useEffect, useState } from "react";
import Link from "next/link";

interface AffiliateDashboardContentProps {
  user: {
    id?: string;
    email?: string | null;
    name?: string | null;
  };
}

interface AffiliateData {
  affiliate: {
    id: number;
    affiliate_code: string;
    status: string;
    tier: string;
    total_clicks: number;
    total_conversions: number;
    total_revenue: number;
    total_commission: number;
    balance: number;
  };
  stats: {
    total_clicks: number;
    total_conversions: number;
    conversion_rate: number;
    total_revenue: number;
    total_commission: number;
    pending_commission: number;
    balance: number;
  };
}

export function AffiliateDashboardContent({ user }: AffiliateDashboardContentProps) {
  const [affiliateData, setAffiliateData] = useState<AffiliateData | null>(null);
  const { loading, execute } = useApiCall<AffiliateData>();

  useEffect(() => {
    if (!user.id) return;

    const loadData = async () => {
      const response = await execute(() => apiClient.getAffiliateProfile(user.id!));
      if (response) {
        setAffiliateData({
          affiliate: response.affiliate,
          stats: response.stats,
        });
      }
    };

    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-sm text-gray-600">データを読み込んでいます...</p>
        </div>
      </div>
    );
  }

  if (!affiliateData) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-gray-600 mb-4">アフィリエイト情報を取得できませんでした。</p>
          <Link href="/affiliate/register" className="text-blue-600 hover:underline font-medium">
            アフィリエイトプログラムに登録する
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-8">
      {/* 統計カード */}
      <AffiliateStatsCards stats={affiliateData.stats} affiliate={affiliateData.affiliate} />

      {/* メインコンテンツグリッド */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 左カラム: リンク管理 */}
        <div className="lg:col-span-2 space-y-8">
          <ReferralLinkManager affiliateId={affiliateData.affiliate.id} />
          <PerformanceChart affiliateId={affiliateData.affiliate.id} />
        </div>

        {/* 右カラム: コミッション履歴 */}
        <div className="space-y-8">
          <CommissionHistory affiliateId={affiliateData.affiliate.id} />
        </div>
      </div>
    </div>
  );
}
