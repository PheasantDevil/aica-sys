import { Footer } from '@/components/footer';
import { Header } from '@/components/header';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">プライバシーポリシー</h1>
        
        <div className="prose prose-gray max-w-none">
          <p className="text-sm text-muted-foreground mb-8">
            最終更新日: 2024年10月11日
          </p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">1. 収集する情報</h2>
            <p className="text-muted-foreground leading-relaxed">
              当サービスは、以下の情報を収集します：
            </p>
            <ul className="list-disc list-inside space-y-2 text-muted-foreground mt-4">
              <li>アカウント情報（メールアドレス、名前）</li>
              <li>利用履歴（閲覧記事、お気に入り）</li>
              <li>サブスクリプション情報</li>
              <li>技術的情報（IPアドレス、ブラウザ情報）</li>
              <li>パフォーマンスメトリクス（Vercel Speed Insights経由、匿名化）</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">2. 情報の利用目的</h2>
            <p className="text-muted-foreground leading-relaxed">
              収集した情報は以下の目的で利用します：
            </p>
            <ul className="list-disc list-inside space-y-2 text-muted-foreground mt-4">
              <li>サービスの提供・改善</li>
              <li>パーソナライズド推薦</li>
              <li>カスタマーサポート</li>
              <li>セキュリティ・不正利用防止</li>
              <li>パフォーマンス測定・最適化（Core Web Vitals）</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">3. 情報の第三者提供</h2>
            <p className="text-muted-foreground leading-relaxed">
              法令に基づく場合を除き、ユーザーの同意なく第三者に個人情報を提供することはありません。
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">4. お問い合わせ</h2>
            <p className="text-muted-foreground leading-relaxed">
              プライバシーに関するお問い合わせ: privacy@aica-sys.com
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}

