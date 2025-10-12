import { Footer } from "@/components/footer";
import { Header } from "@/components/header";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8">ドキュメント</h1>

        <div className="grid gap-8 lg:grid-cols-4">
          <aside className="lg:col-span-1">
            <nav className="space-y-2">
              <a href="#getting-started" className="block p-2 rounded hover:bg-muted">
                はじめに
              </a>
              <a href="#features" className="block p-2 rounded hover:bg-muted">
                主要機能
              </a>
              <a href="#api" className="block p-2 rounded hover:bg-muted">
                API
              </a>
              <a href="#faq" className="block p-2 rounded hover:bg-muted">
                FAQ
              </a>
            </nav>
          </aside>

          <div className="lg:col-span-3 space-y-8">
            <section id="getting-started">
              <h2 className="text-2xl font-semibold mb-4">はじめに</h2>
              <p className="text-muted-foreground leading-relaxed">
                AICA-SySは、AI駆動型のコンテンツ自動生成プラットフォームです。
                最新の技術トレンドを自動で収集・分析し、高品質な記事を生成します。
              </p>
            </section>

            <section id="features">
              <h2 className="text-2xl font-semibold mb-4">主要機能</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-medium mb-2">デイリー記事生成</h3>
                  <p className="text-muted-foreground">
                    平日毎日、最新トレンドを分析して3-5記事を自動生成します。
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-medium mb-2">トレンド分析</h3>
                  <p className="text-muted-foreground">
                    複数ソースから情報を収集し、リアルタイムでトレンドを分析します。
                  </p>
                </div>
                <div>
                  <h3 className="text-xl font-medium mb-2">週次ニュースレター</h3>
                  <p className="text-muted-foreground">
                    毎週月曜日、週間トレンドまとめをお届けします。
                  </p>
                </div>
              </div>
            </section>

            <section id="api">
              <h2 className="text-2xl font-semibold mb-4">API</h2>
              <p className="text-muted-foreground leading-relaxed">
                REST API を提供しています。詳細は API ドキュメントをご覧ください。
              </p>
            </section>

            <section id="faq">
              <h2 className="text-2xl font-semibold mb-4">よくある質問</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-medium mb-2">無料プランでできることは？</h3>
                  <p className="text-muted-foreground">
                    月10記事まで閲覧可能です。トレンド分析は無制限でご利用いただけます。
                  </p>
                </div>
                <div>
                  <h3 className="text-lg font-medium mb-2">コンテンツの更新頻度は？</h3>
                  <p className="text-muted-foreground">
                    記事は平日毎日、トレンドは毎日、ニュースレターは毎週更新されます。
                  </p>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
