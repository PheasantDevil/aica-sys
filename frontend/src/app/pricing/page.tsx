"use client";

import { Footer } from "@/components/footer";
import { Header } from "@/components/header";
import { SubscriptionCard } from "@/components/subscription/subscription-card";
import { useSubscription } from "@/hooks/use-subscription";
import { useSession } from "next-auth/react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";

function PricingContent() {
  const { data: session } = useSession();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { subscription, handleUpgrade, handleContact, isUpgrading } = useSubscription();

  // サインイン後、選択されていたプランがあれば自動的に決済に進む
  useEffect(() => {
    const selectedPlan = searchParams.get("plan");

    if (session && selectedPlan && !isUpgrading) {
      // プランパラメータをクリア
      router.replace("/pricing");

      // 選択されたプランに応じて処理
      if (selectedPlan === "PREMIUM" && process.env.NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID) {
        handleUpgrade(process.env.NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID);
      } else if (selectedPlan === "ENTERPRISE") {
        handleContact();
      } else if (selectedPlan === "FREE") {
        router.push("/dashboard");
      }
    }
  }, [session, searchParams, handleUpgrade, handleContact, isUpgrading, router]);

  const handleSelectPlan = (plan: "FREE" | "PREMIUM" | "ENTERPRISE") => {
    if (!session) {
      // 選択したプランをクエリパラメータに含めてサインインページへ
      const returnUrl = `/pricing?plan=${plan}`;
      router.push(`/auth/signin?callbackUrl=${encodeURIComponent(returnUrl)}`);
      return;
    }

    if (plan === "FREE") {
      router.push("/dashboard");
      return;
    }

    if (plan === "ENTERPRISE") {
      handleContact();
      return;
    }

    if (plan === "PREMIUM" && process.env.NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID) {
      handleUpgrade(process.env.NEXT_PUBLIC_STRIPE_PREMIUM_PRICE_ID);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container py-20">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6">料金プラン</h1>
          <p className="text-lg text-muted-foreground sm:text-xl">
            あなたのニーズに合わせたプランを選択してください
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <SubscriptionCard
            plan="FREE"
            isCurrentPlan={subscription?.plan === "free"}
            onSelect={() => handleSelectPlan("FREE")}
            loading={isUpgrading}
          />
          <SubscriptionCard
            plan="PREMIUM"
            isCurrentPlan={subscription?.plan === "premium"}
            isPopular={true}
            onSelect={() => handleSelectPlan("PREMIUM")}
            loading={isUpgrading}
          />
          <SubscriptionCard
            plan="ENTERPRISE"
            isCurrentPlan={subscription?.plan === "enterprise"}
            onSelect={() => handleSelectPlan("ENTERPRISE")}
            loading={isUpgrading}
          />
        </div>

        <div className="mt-16 text-center">
          <p className="text-sm text-muted-foreground">
            すべてのプランには14日間の無料トライアルが含まれます
          </p>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default function PricingPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-background">
          <Header />
          <main className="container py-20">
            <div className="mx-auto max-w-2xl text-center mb-16">
              <h1 className="text-4xl font-bold tracking-tight sm:text-6xl mb-6">料金プラン</h1>
              <p className="text-lg text-muted-foreground sm:text-xl">読み込み中...</p>
            </div>
          </main>
          <Footer />
        </div>
      }
    >
      <PricingContent />
    </Suspense>
  );
}
