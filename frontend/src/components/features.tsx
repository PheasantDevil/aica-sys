import { CheckCircle, Zap, Shield, BarChart3 } from 'lucide-react'

export function Features() {
  const features = [
    {
      title: "完全自動化",
      description: "情報収集からコンテンツ生成、公開まで全て自動で実行",
      icon: Zap,
    },
    {
      title: "高品質コンテンツ",
      description: "AIが生成する技術記事は専門性と読みやすさを両立",
      icon: CheckCircle,
    },
    {
      title: "セキュア",
      description: "企業レベルのセキュリティでデータを保護",
      icon: Shield,
    },
    {
      title: "詳細分析",
      description: "収益、エンゲージメント、コンテンツ品質を詳細に分析",
      icon: BarChart3,
    },
  ]

  return (
    <section className="py-20">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight sm:text-4xl">
            なぜAICA-SySなのか
          </h2>
          <p className="text-lg text-muted-foreground">
            TypeScript開発者向けに特化した、次世代のコンテンツ自動生成プラットフォーム
          </p>
        </div>
        
        <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div key={feature.title} className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
