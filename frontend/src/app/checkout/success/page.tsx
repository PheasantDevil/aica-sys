"use client";

import { Footer } from "@/components/footer";
import { Header } from "@/components/header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, Check, Crown, Sparkles } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const sessionIdParam = searchParams.get("session_id");
    setSessionId(sessionIdParam);
    setIsLoading(false);
  }, [searchParams]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container py-20">
          <div className="flex items-center justify-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container py-20">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-8">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-100">
              <Check className="h-10 w-10 text-green-600" />
            </div>

            <h1 className="text-4xl font-bold tracking-tight mb-4">お支払いが完了しました！</h1>

            <p className="text-xl text-muted-foreground mb-8">
              プレミアムプランへのアップグレードが正常に完了しました。
              今すぐすべての機能をご利用いただけます。
            </p>
          </div>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center justify-center gap-2">
                <Crown className="h-5 w-5 text-yellow-500" />
                プレミアムプランがアクティブ
              </CardTitle>
              <CardDescription>お支払いが正常に処理されました</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                  <span className="font-medium">サブスクリプション</span>
                  <Badge className="bg-green-600 text-white">
                    <Check className="h-3 w-3 mr-1" />
                    アクティブ
                  </Badge>
                </div>

                {sessionId && (
                  <div className="text-sm text-muted-foreground">セッションID: {sessionId}</div>
                )}
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="p-3 bg-blue-100 rounded-full">
                    <Sparkles className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
                <h3 className="font-semibold mb-2">プレミアム機能</h3>
                <p className="text-sm text-muted-foreground">
                  すべてのプレミアム機能にアクセスできます
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="p-3 bg-green-100 rounded-full">
                    <Check className="h-6 w-6 text-green-600" />
                  </div>
                </div>
                <h3 className="font-semibold mb-2">即座にアクティベート</h3>
                <p className="text-sm text-muted-foreground">
                  今すぐプレミアムコンテンツをご利用いただけます
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-center mb-4">
                  <div className="p-3 bg-purple-100 rounded-full">
                    <Crown className="h-6 w-6 text-purple-600" />
                  </div>
                </div>
                <h3 className="font-semibold mb-2">優先サポート</h3>
                <p className="text-sm text-muted-foreground">専用サポートチームがサポートします</p>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-4">
            <Button size="lg" asChild>
              <Link href="/dashboard">
                ダッシュボードに移動
                <ArrowRight className="h-4 w-4 ml-2" />
              </Link>
            </Button>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="outline" asChild>
                <Link href="/articles">記事を読む</Link>
              </Button>

              <Button variant="outline" asChild>
                <Link href="/trends">トレンドを確認</Link>
              </Button>

              <Button variant="outline" asChild>
                <Link href="/settings">設定を確認</Link>
              </Button>
            </div>
          </div>

          <div className="mt-12 p-6 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2">次に何をしますか？</h3>
            <p className="text-sm text-muted-foreground mb-4">
              プレミアムプランにアップグレードしたので、以下の機能をご利用いただけます：
            </p>
            <ul className="text-sm text-muted-foreground space-y-1 text-left max-w-md mx-auto">
              <li>• 日次トレンドレポートの受信</li>
              <li>• 全記事の無制限アクセス</li>
              <li>• プレミアムコンテンツの閲覧</li>
              <li>• API アクセス</li>
              <li>• カスタム分析機能</li>
            </ul>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-background">
          <Header />
          <main className="container py-20">
            <div className="flex items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            </div>
          </main>
          <Footer />
        </div>
      }
    >
      <CheckoutSuccessContent />
    </Suspense>
  );
}
