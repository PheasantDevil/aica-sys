"use client";

import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { TrendCard } from "@/components/content/trend-card";
import { TrendFilters } from "@/components/content/trend-filters";
import { useTrends } from "@/hooks/use-trends";
import { Button } from "@/components/ui/button";
import { Plus, TrendingUp } from "lucide-react";
import { useState } from "react";

export default function TrendsPage() {
  const [filters, setFilters] = useState({
    timeframe: "week",
    category: "all",
    sortBy: "trending",
  });

  const { trends, isLoading, error } = useTrends(filters);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">トレンド分析</h1>
              <p className="text-muted-foreground">TypeScriptエコシステムの最新トレンドと分析</p>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新しい分析
            </Button>
          </div>

          <TrendFilters filters={filters} onFiltersChange={setFilters} />
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-64 animate-pulse bg-muted rounded-lg"></div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">トレンドの読み込みに失敗しました</p>
            <Button variant="outline" className="mt-4">
              再試行
            </Button>
          </div>
        ) : trends.length === 0 ? (
          <div className="text-center py-12">
            <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">トレンドが見つかりません</h3>
            <p className="text-muted-foreground mb-4">フィルター条件を変更してお試しください</p>
            <Button variant="outline">フィルターをリセット</Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {trends.map((trend) => (
              <TrendCard key={trend.id} trend={trend} />
            ))}
          </div>
        )}

        {trends.length > 0 && (
          <div className="mt-12 text-center">
            <Button variant="outline">さらに読み込む</Button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
