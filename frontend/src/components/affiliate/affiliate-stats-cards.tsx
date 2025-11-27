"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, MousePointerClick, DollarSign, Wallet } from "lucide-react";

interface AffiliateStatsCardsProps {
  stats: {
    total_clicks: number;
    total_conversions: number;
    conversion_rate: number;
    total_revenue: number;
    total_commission: number;
    pending_commission: number;
    balance: number;
  };
  affiliate: {
    tier: string;
    affiliate_code: string;
  };
}

export function AffiliateStatsCards({ stats, affiliate }: AffiliateStatsCardsProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
    }).format(amount);
  };

  const formatPercentage = (value: number) => {
    return `${value.toFixed(2)}%`;
  };

  const statsCards = [
    {
      title: "総クリック数",
      value: stats.total_clicks.toLocaleString(),
      icon: MousePointerClick,
      description: "累計クリック数",
      color: "text-blue-600",
    },
    {
      title: "総コンバージョン数",
      value: stats.total_conversions.toLocaleString(),
      icon: TrendingUp,
      description: `コンバージョン率: ${formatPercentage(stats.conversion_rate)}`,
      color: "text-green-600",
    },
    {
      title: "総収益",
      value: formatCurrency(stats.total_revenue),
      icon: DollarSign,
      description: "累計紹介収益",
      color: "text-purple-600",
    },
    {
      title: "未払い残高",
      value: formatCurrency(stats.balance),
      icon: Wallet,
      description: `ティア: ${affiliate.tier}`,
      color: "text-orange-600",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statsCards.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <Icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">{stat.description}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
