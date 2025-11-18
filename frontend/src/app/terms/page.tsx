import { Footer } from "@/components/footer";
import { Header } from "@/components/header";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        <h1 className="text-4xl font-bold mb-8">利用規約</h1>

        <div className="prose prose-gray max-w-none">
          <p className="text-sm text-muted-foreground mb-8">最終更新日: 2024年10月11日</p>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">第1条（適用）</h2>
            <p className="text-muted-foreground leading-relaxed">
              本規約は、AICA-SySが提供するサービスの利用条件を定めるものです。
              ユーザーは本規約に同意の上、サービスを利用するものとします。
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">第2条（アカウント）</h2>
            <p className="text-muted-foreground leading-relaxed">
              ユーザーは、正確な情報を登録し、アカウント情報を適切に管理する責任を負います。
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">第3条（禁止事項）</h2>
            <p className="text-muted-foreground leading-relaxed">以下の行為を禁止します：</p>
            <ul className="list-disc list-inside space-y-2 text-muted-foreground mt-4">
              <li>法令または公序良俗に違反する行為</li>
              <li>当社または第三者の権利を侵害する行為</li>
              <li>サービスの運営を妨害する行為</li>
              <li>不正アクセスまたはこれに類する行為</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">第4条（サブスクリプション）</h2>
            <p className="text-muted-foreground leading-relaxed">
              有料プランは月額または年額の定期課金となります。
              キャンセルは期間終了までに行う必要があります。
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">第5条（免責事項）</h2>
            <p className="text-muted-foreground leading-relaxed">
              当社は、サービスの正確性、完全性、有用性について保証しません。
              サービス利用により生じた損害について、当社は責任を負いません。
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold mb-4">第6条（お問い合わせ）</h2>
            <p className="text-muted-foreground leading-relaxed">
              利用規約に関するお問い合わせ: legal@aica-sys.com
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </div>
  );
}
