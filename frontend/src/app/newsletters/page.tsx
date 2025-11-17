"use client";

import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { NewsletterCard } from "@/components/content/newsletter-card";
import { useNewsletters } from "@/hooks/use-newsletters";
import { Button } from "@/components/ui/button";
import { Plus, Mail } from "lucide-react";

export default function NewslettersPage() {
  const { newsletters, isLoading, error } = useNewsletters();

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">ニュースレター</h1>
              <p className="text-muted-foreground">TypeScriptエコシステムの最新情報をお届け</p>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新しいニュースレター
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-64 animate-pulse bg-muted rounded-lg"></div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">ニュースレターの読み込みに失敗しました</p>
            <Button variant="outline" className="mt-4">
              再試行
            </Button>
          </div>
        ) : newsletters.length === 0 ? (
          <div className="text-center py-12">
            <Mail className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">ニュースレターがありません</h3>
            <p className="text-muted-foreground mb-4">新しいニュースレターを作成してください</p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新しいニュースレター
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {newsletters.map((newsletter) => (
              <NewsletterCard key={newsletter.id} newsletter={newsletter} />
            ))}
          </div>
        )}

        {newsletters.length > 0 && (
          <div className="mt-12 text-center">
            <Button variant="outline">さらに読み込む</Button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
