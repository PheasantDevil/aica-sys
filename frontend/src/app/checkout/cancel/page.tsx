'use client';

import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { X, ArrowLeft, RefreshCw } from 'lucide-react';
import Link from 'next/link';

export default function CheckoutCancelPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container py-20">
        <div className="max-w-2xl mx-auto text-center">
          <div className="mb-8">
            <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-100">
              <X className="h-10 w-10 text-red-600" />
            </div>
            
            <h1 className="text-4xl font-bold tracking-tight mb-4">
              お支払いがキャンセルされました
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8">
              お支払いプロセスが中断されました。
              いつでも再度お試しください。
            </p>
          </div>

          <Card className="mb-8">
            <CardHeader>
              <CardTitle>お支払いが完了しませんでした</CardTitle>
              <CardDescription>
                お支払いプロセスが中断されました。心配ありません。
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-yellow-800">
                    <strong>重要：</strong> お支払いは処理されていません。
                    クレジットカードに料金は請求されません。
                  </p>
                </div>
                
                <div className="text-sm text-muted-foreground">
                  <p>お支払いが完了しなかった理由：</p>
                  <ul className="mt-2 space-y-1 text-left max-w-md mx-auto">
                    <li>• ブラウザを閉じた</li>
                    <li>• ネットワーク接続の問題</li>
                    <li>• お支払い情報の入力エラー</li>
                    <li>• 意図的なキャンセル</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <Button size="lg" asChild>
              <Link href="/pricing">
                <RefreshCw className="h-4 w-4 mr-2" />
                再度お支払いを試す
              </Link>
            </Button>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="outline" asChild>
                <Link href="/dashboard">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  ダッシュボードに戻る
                </Link>
              </Button>
              
              <Button variant="outline" asChild>
                <Link href="/articles">
                  記事を読む
                </Link>
              </Button>
            </div>
          </div>

          <div className="mt-12 p-6 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2">サポートが必要ですか？</h3>
            <p className="text-sm text-muted-foreground mb-4">
              お支払いに関するご質問やサポートが必要な場合は、お気軽にお問い合わせください。
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="outline" size="sm" asChild>
                <Link href="/help">
                  ヘルプセンター
                </Link>
              </Button>
              
              <Button variant="outline" size="sm" asChild>
                <Link href="/contact">
                  お問い合わせ
                </Link>
              </Button>
            </div>
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">フリープランでお試しください</h4>
            <p className="text-sm text-blue-800 mb-3">
              プレミアムプランにアップグレードする前に、フリープランでサービスをお試しください。
            </p>
            <Button variant="outline" size="sm" asChild>
              <Link href="/dashboard">
                フリープランで開始
              </Link>
            </Button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
