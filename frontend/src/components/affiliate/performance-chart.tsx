"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp } from "lucide-react";

interface PerformanceChartProps {
  affiliateId: number;
}

export function PerformanceChart({ affiliateId }: PerformanceChartProps) {
  // TODO: 実際のデータをAPIから取得してグラフを表示
  // 現在はプレースホルダー表示

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>パフォーマンス分析</CardTitle>
            <CardDescription>クリック数とコンバージョン数の推移</CardDescription>
          </div>
          <TrendingUp className="h-5 w-5 text-gray-400" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <p className="text-sm">グラフ表示機能は今後実装予定です</p>
            <p className="text-xs mt-2">時系列データの可視化</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
