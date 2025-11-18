"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useSubscription } from "@/hooks/use-subscription";
import { CreditCard, Calendar, Crown, ExternalLink, Settings, AlertTriangle } from "lucide-react";
import Link from "next/link";
import { format } from "date-fns";
import { ja } from "date-fns/locale";

export function AccountSettings() {
  const { subscription, isLoading } = useSubscription();

  const getPlanInfo = (plan: string) => {
    switch (plan) {
      case "premium":
        return {
          name: "プレミアムプラン",
          color: "bg-primary",
          icon: Crown,
          description: "すべての機能にアクセス",
        };
      case "enterprise":
        return {
          name: "エンタープライズプラン",
          color: "bg-purple-500",
          icon: Crown,
          description: "カスタムソリューション",
        };
      default:
        return {
          name: "フリープラン",
          color: "bg-muted",
          icon: Settings,
          description: "基本的な機能",
        };
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="p-6">
            <div className="h-32 animate-pulse bg-muted rounded"></div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const planInfo = getPlanInfo(subscription?.plan || "free");
  const Icon = planInfo.icon;

  return (
    <div className="space-y-6">
      {/* サブスクリプション情報 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            サブスクリプション
          </CardTitle>
          <CardDescription>現在のプランと請求情報</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${planInfo.color} text-white`}>
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <p className="font-medium">{planInfo.name}</p>
                <p className="text-sm text-muted-foreground">{planInfo.description}</p>
              </div>
            </div>

            <div className="text-right">
              <Badge
                variant={subscription?.status === "active" ? "default" : "secondary"}
                className={subscription?.status === "active" ? "bg-green-600" : ""}
              >
                {subscription?.status === "active" ? "アクティブ" : "非アクティブ"}
              </Badge>
            </div>
          </div>

          {subscription?.stripeCurrentPeriodEnd && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>
                次回更新日:{" "}
                {format(new Date(subscription.stripeCurrentPeriodEnd), "yyyy年M月d日", {
                  locale: ja,
                })}
              </span>
            </div>
          )}

          <Separator />

          <div className="flex gap-2">
            {subscription?.plan === "free" ? (
              <Button asChild>
                <Link href="/pricing">
                  <Crown className="h-4 w-4 mr-2" />
                  アップグレード
                </Link>
              </Button>
            ) : (
              <Button variant="outline" asChild>
                <Link href="/checkout">
                  <Settings className="h-4 w-4 mr-2" />
                  プランを変更
                </Link>
              </Button>
            )}

            {subscription?.stripeCustomerId && (
              <Button variant="outline" asChild>
                <Link href="/billing">
                  <ExternalLink className="h-4 w-4 mr-2" />
                  請求を管理
                </Link>
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 請求履歴 */}
      <Card>
        <CardHeader>
          <CardTitle>請求履歴</CardTitle>
          <CardDescription>過去の請求と支払い履歴</CardDescription>
        </CardHeader>
        <CardContent>
          {subscription?.plan === "free" ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">フリープランのため、請求履歴はありません</p>
              <Button asChild>
                <Link href="/pricing">プレミアムプランにアップグレード</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {/* モックデータ - 実際の実装ではAPIから取得 */}
              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">プレミアムプラン - 2024年1月</p>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date("2024-01-15"), "yyyy年M月d日", { locale: ja })}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">¥1,980</p>
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    支払い済み
                  </Badge>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">プレミアムプラン - 2023年12月</p>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date("2023-12-15"), "yyyy年M月d日", { locale: ja })}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-medium">¥1,980</p>
                  <Badge variant="outline" className="text-green-600 border-green-600">
                    支払い済み
                  </Badge>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* アカウント管理 */}
      <Card>
        <CardHeader>
          <CardTitle>アカウント管理</CardTitle>
          <CardDescription>アカウントの削除とデータ管理</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-medium text-yellow-800">アカウントの削除</p>
                <p className="text-sm text-yellow-700 mt-1">
                  アカウントを削除すると、すべてのデータが永久に削除されます。
                  この操作は元に戻すことができません。
                </p>
                <Button variant="destructive" size="sm" className="mt-3" disabled>
                  アカウントを削除
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
