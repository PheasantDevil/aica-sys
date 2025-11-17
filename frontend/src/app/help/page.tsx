import { Footer } from "@/components/footer";
import { Header } from "@/components/header";

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold mb-8">ヘルプセンター</h1>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-4">はじめに</h2>
            <p className="text-muted-foreground mb-4">AICA-SySの基本的な使い方をご紹介します。</p>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-4">記事の閲覧</h2>
            <p className="text-muted-foreground mb-4">
              最新の技術記事を閲覧する方法について説明します。
            </p>
          </div>

          <div className="p-6 border rounded-lg">
            <h2 className="text-xl font-semibold mb-4">サブスクリプション</h2>
            <p className="text-muted-foreground mb-4">
              プラン選択、支払い、アップグレード方法をご案内します。
            </p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
