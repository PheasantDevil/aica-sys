import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, TrendingUp, Users } from "lucide-react";

export function Hero() {
  return (
    <section className="relative py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-8 flex justify-center">
            <div className="relative rounded-full border bg-muted px-4 py-2 text-sm">
              <Sparkles className="mr-2 inline h-4 w-4" />
              TypeScriptエコシステム特化型AI
            </div>
          </div>

          <h1 className="mb-6 text-4xl font-bold tracking-tight sm:text-6xl">
            AI駆動型コンテンツ
            <span className="text-primary">自動生成システム</span>
          </h1>

          <p className="mb-8 text-lg text-muted-foreground sm:text-xl">
            TypeScriptの最新動向を自動収集・分析し、 高品質なコンテンツを自動生成・販売する
            完全自動化プラットフォーム
          </p>

          <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button size="lg" className="text-lg px-8">
              無料で始める
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8">
              デモを見る
            </Button>
          </div>

          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-3">
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <TrendingUp className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">自動トレンド分析</h3>
              <p className="text-sm text-muted-foreground">
                TypeScriptエコシステムの最新動向を24時間365日監視
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">AI自動生成</h3>
              <p className="text-sm text-muted-foreground">
                Gemini APIを活用した高品質なコンテンツ自動生成
              </p>
            </div>

            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <Users className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">収益化</h3>
              <p className="text-sm text-muted-foreground">
                月額サブスクリプションで安定した収益を実現
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
