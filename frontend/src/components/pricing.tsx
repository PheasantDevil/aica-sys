import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

export function Pricing() {
  const plans = [
    {
      name: "フリー",
      price: "¥0",
      period: "月",
      description: "基本的な機能をお試しください",
      features: [
        "週1回のトレンドレポート",
        "基本記事の閲覧",
        "コミュニティアクセス",
        "メールサポート",
      ],
      cta: "無料で始める",
      popular: false,
    },
    {
      name: "プレミアム",
      price: "¥1,980",
      period: "月",
      description: "本格的なTypeScript開発者向け",
      features: [
        "日次トレンドレポート",
        "全記事の閲覧",
        "プレミアムコンテンツ",
        "優先サポート",
        "API アクセス",
        "カスタム分析",
      ],
      cta: "プレミアムを開始",
      popular: true,
    },
    {
      name: "エンタープライズ",
      price: "カスタム",
      period: "",
      description: "チーム・企業向けソリューション",
      features: [
        "無制限アクセス",
        "チーム管理機能",
        "カスタムブランディング",
        "専任サポート",
        "オンプレミス対応",
        "SLA保証",
      ],
      cta: "お問い合わせ",
      popular: false,
    },
  ];

  return (
    <section className="py-20">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">料金プラン</h2>
          <p className="text-lg text-muted-foreground">
            あなたのニーズに合わせたプランを選択してください
          </p>
        </div>

        <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative rounded-lg border p-8 ${
                plan.popular ? "border-primary bg-primary/5" : "border-border"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="rounded-full bg-primary px-4 py-1 text-sm font-medium text-primary-foreground">
                    人気
                  </span>
                </div>
              )}

              <div className="text-center">
                <h3 className="text-xl font-semibold">{plan.name}</h3>
                <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
                <div className="mt-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  {plan.period && <span className="text-muted-foreground">/{plan.period}</span>}
                </div>
              </div>

              <ul className="mt-8 space-y-4">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start">
                    <Check className="mr-3 h-5 w-5 flex-shrink-0 text-primary" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <div className="mt-8">
                <Button className="w-full" variant={plan.popular ? "default" : "outline"}>
                  {plan.cta}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
