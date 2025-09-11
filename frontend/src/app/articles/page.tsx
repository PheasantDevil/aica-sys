'use client';

import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { ArticleCard } from '@/components/content/article-card';
import { ArticleFilters } from '@/components/content/article-filters';
import { useArticles } from '@/hooks/use-articles';
import { Button } from '@/components/ui/button';
import { Plus, Search } from 'lucide-react';
import { useState } from 'react';

export default function ArticlesPage() {
  const [filters, setFilters] = useState({
    category: 'all',
    sortBy: 'newest',
    search: '',
  });
  
  const { articles, isLoading, error } = useArticles(filters);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">記事</h1>
              <p className="text-muted-foreground">
                TypeScriptに関する最新の記事とチュートリアル
              </p>
            </div>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              新しい記事
            </Button>
          </div>
          
          <ArticleFilters 
            filters={filters}
            onFiltersChange={setFilters}
          />
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-64 animate-pulse bg-muted rounded-lg"></div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">記事の読み込みに失敗しました</p>
            <Button variant="outline" className="mt-4">
              再試行
            </Button>
          </div>
        ) : articles.length === 0 ? (
          <div className="text-center py-12">
            <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">記事が見つかりません</h3>
            <p className="text-muted-foreground mb-4">
              検索条件を変更してお試しください
            </p>
            <Button variant="outline">
              フィルターをリセット
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>
        )}

        {articles.length > 0 && (
          <div className="mt-12 text-center">
            <Button variant="outline">
              さらに読み込む
            </Button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}