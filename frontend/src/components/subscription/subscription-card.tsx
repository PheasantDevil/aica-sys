"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PLANS, PlanType } from "@/lib/subscription";
import { Check, Crown, Zap } from "lucide-react";

interface SubscriptionCardProps {
  plan: PlanType;
  isCurrentPlan?: boolean;
  isPopular?: boolean;
  onSelect?: () => void;
  loading?: boolean;
}

export function SubscriptionCard({
  plan,
  isCurrentPlan = false,
  isPopular = false,
  onSelect,
  loading = false,
}: SubscriptionCardProps) {
  const planData = PLANS[plan];

  return (
    <Card className={`relative ${isPopular ? "border-primary bg-primary/5" : ""}`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <Badge className="bg-primary text-primary-foreground">
            <Crown className="h-3 w-3 mr-1" />
            人気
          </Badge>
        </div>
      )}

      <CardHeader className="text-center">
        <CardTitle className="text-xl">{planData.name}</CardTitle>
        <CardDescription>
          {plan === "ENTERPRISE"
            ? "チーム・企業向けソリューション"
            : plan === "PREMIUM"
            ? "本格的なTypeScript開発者向け"
            : "基本的な機能をお試しください"}
        </CardDescription>
        <div className="mt-4">
          {plan === "ENTERPRISE" ? (
            <span className="text-4xl font-bold">カスタム</span>
          ) : (
            <>
              <span className="text-4xl font-bold">¥{planData.price.toLocaleString()}</span>
              <span className="text-muted-foreground">/月</span>
            </>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <ul className="space-y-3">
          {planData.features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="h-5 w-5 text-primary mr-3 flex-shrink-0 mt-0.5" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>

        <div className="pt-4">
          {isCurrentPlan ? (
            <Button disabled className="w-full">
              <Check className="h-4 w-4 mr-2" />
              現在のプラン
            </Button>
          ) : plan === "ENTERPRISE" ? (
            <Button variant="outline" className="w-full" onClick={onSelect}>
              お問い合わせ
            </Button>
          ) : (
            <Button className="w-full" onClick={onSelect} disabled={loading}>
              {loading ? (
                <>
                  <Zap className="h-4 w-4 mr-2 animate-spin" />
                  処理中...
                </>
              ) : (
                <>{plan === "FREE" ? "無料で始める" : "プレミアムを開始"}</>
              )}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
