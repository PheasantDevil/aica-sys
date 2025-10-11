import { Footer } from '@/components/footer';
import { Header } from '@/components/header';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">会社概要</h1>
        
        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">AICA-SySについて</h2>
            <p className="text-muted-foreground leading-relaxed">
              AICA-SyS（AI Content Automation System）は、AI駆動型のコンテンツ自動生成・配信プラットフォームです。
              最新の技術トレンドを自動で分析し、高品質な記事、ニュースレター、トレンド分析レポートを提供します。
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">ミッション</h2>
            <p className="text-muted-foreground leading-relaxed">
              技術者が最新情報をキャッチアップする時間を削減し、本質的な開発作業に集中できる環境を提供します。
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">主な機能</h2>
            <ul className="list-disc list-inside space-y-2 text-muted-foreground">
              <li>AIによる自動記事生成（平日毎日）</li>
              <li>リアルタイムトレンド分析（毎日更新）</li>
              <li>週次ニュースレター配信</li>
              <li>パーソナライズド推薦</li>
              <li>コンテンツ品質評価</li>
            </ul>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}

