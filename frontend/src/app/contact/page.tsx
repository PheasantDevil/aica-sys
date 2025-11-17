import { Footer } from "@/components/footer";
import { Header } from "@/components/header";

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-16 max-w-2xl">
        <h1 className="text-4xl font-bold mb-8">お問い合わせ</h1>

        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-semibold mb-4">サポート</h2>
            <p className="text-muted-foreground mb-2">Email: support@aica-sys.com</p>
            <p className="text-muted-foreground">営業時間: 平日 9:00-18:00（JST）</p>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4">営業・提携</h2>
            <p className="text-muted-foreground">Email: business@aica-sys.com</p>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4">技術的なお問い合わせ</h2>
            <p className="text-muted-foreground">Email: tech@aica-sys.com</p>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
