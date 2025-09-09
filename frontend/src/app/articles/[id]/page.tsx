'use client';

import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  ArrowLeft,
  Bookmark,
  Calendar,
  Clock,
  Eye,
  Share2,
  Star,
  Tag,
  User,
} from 'lucide-react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';

export default function ArticleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(89);

  // モックデータ（実際の実装ではAPIから取得）
  const article = {
    id: 1,
    title: 'TypeScript 5.0の新機能とベストプラクティス',
    content: `
# TypeScript 5.0の新機能とベストプラクティス

TypeScript 5.0は、TypeScriptの最新メジャーバージョンとして、多くの新機能と改善が導入されました。本記事では、これらの新機能を詳しく解説し、実際のプロジェクトでの活用法を紹介します。

## 主な新機能

### 1. const アサーションの改善

TypeScript 5.0では、const アサーションがより強力になりました。

\`\`\`typescript
// 以前
const colors = ['red', 'green', 'blue'] as const;

// 5.0以降
const colors = ['red', 'green', 'blue'] as const;
// より厳密な型推論
\`\`\`

### 2. デコレータの正式サポート

デコレータが正式にサポートされ、より安全で予測可能な動作を提供します。

\`\`\`typescript
function logged(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  
  descriptor.value = function(...args: any[]) {
    console.log(\`Calling \${propertyKey} with args:\`, args);
    return originalMethod.apply(this, args);
  };
  
  return descriptor;
}

class Calculator {
  @logged
  add(a: number, b: number): number {
    return a + b;
  }
}
\`\`\`

### 3. 型の改善

多くの型システムの改善により、より正確な型推論が可能になりました。

## ベストプラクティス

### 1. 型の明確化

新しい型システムを活用して、より明確な型定義を行いましょう。

\`\`\`typescript
// 良い例
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
}

// より良い例（5.0の新機能を活用）
type User = {
  readonly id: string;
  name: string;
  email: string;
  readonly createdAt: Date;
} & {
  updateProfile(updates: Partial<Pick<User, 'name' | 'email'>>): void;
};
\`\`\`

### 2. パフォーマンスの最適化

TypeScript 5.0の改善により、コンパイル時間が大幅に短縮されました。

## まとめ

TypeScript 5.0は、開発者体験を大幅に改善する多くの新機能を提供します。これらの機能を適切に活用することで、より安全で保守性の高いコードを書くことができます。

今後のプロジェクトでは、これらの新機能を積極的に取り入れ、TypeScriptの真の力を発揮しましょう。
    `,
    author: 'AICA Team',
    publishedAt: '2024-09-08',
    readTime: '8分',
    views: 1234,
    likes: 89,
    category: 'TypeScript',
    tags: ['TypeScript', 'JavaScript', 'Tutorial'],
    featured: true,
  };

  const relatedArticles = [
    {
      id: 2,
      title: 'Next.js 14 App Router完全ガイド',
      excerpt:
        'Next.js 14のApp Routerの基本から応用まで、実践的な使い方をステップバイステップで解説します。',
      publishedAt: '2024-09-07',
      readTime: '12分',
      views: 987,
      category: 'Next.js',
    },
    {
      id: 3,
      title: 'React Server Componentsの実践的活用法',
      excerpt:
        'React Server Componentsの概念から実装まで、パフォーマンス向上のための具体的な手法を紹介します。',
      publishedAt: '2024-09-06',
      readTime: '10分',
      views: 756,
      category: 'React',
    },
    {
      id: 4,
      title: 'TypeScript型安全性の向上テクニック',
      excerpt:
        'TypeScriptでより安全なコードを書くための高度なテクニックとパターンを詳しく解説します。',
      publishedAt: '2024-09-05',
      readTime: '6分',
      views: 543,
      category: 'TypeScript',
    },
  ];

  const getCategoryBadge = (category: string) => {
    const colors = {
      TypeScript: 'bg-blue-100 text-blue-800',
      'Next.js': 'bg-green-100 text-green-800',
      React: 'bg-cyan-100 text-cyan-800',
      'Build Tools': 'bg-purple-100 text-purple-800',
    };
    return (
      <Badge
        className={
          colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800'
        }
      >
        {category}
      </Badge>
    );
  };

  const handleLike = () => {
    setIsLiked(!isLiked);
    setLikeCount(prev => (isLiked ? prev - 1 : prev + 1));
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: article.title,
          text: article.content.substring(0, 100) + '...',
          url: window.location.href,
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      // フォールバック: クリップボードにコピー
      navigator.clipboard.writeText(window.location.href);
    }
  };

  return (
    <div className='min-h-screen bg-background'>
      <Header />

      <main className='container py-8'>
        {/* 戻るボタン */}
        <div className='mb-6'>
          <Button
            variant='outline'
            onClick={() => router.back()}
            className='flex items-center gap-2'
          >
            <ArrowLeft className='h-4 w-4' />
            記事一覧に戻る
          </Button>
        </div>

        <div className='grid grid-cols-1 lg:grid-cols-4 gap-8'>
          {/* メインコンテンツ */}
          <article className='lg:col-span-3'>
            {/* 記事ヘッダー */}
            <header className='mb-8'>
              <div className='flex items-center gap-2 mb-4'>
                {getCategoryBadge(article.category)}
                {article.featured && (
                  <Badge className='bg-yellow-100 text-yellow-800'>
                    おすすめ
                  </Badge>
                )}
              </div>

              <h1 className='text-4xl font-bold text-foreground mb-4'>
                {article.title}
              </h1>

              <div className='flex items-center justify-between text-sm text-muted-foreground mb-6'>
                <div className='flex items-center gap-6'>
                  <div className='flex items-center gap-2'>
                    <User className='h-4 w-4' />
                    {article.author}
                  </div>
                  <div className='flex items-center gap-2'>
                    <Calendar className='h-4 w-4' />
                    {article.publishedAt}
                  </div>
                  <div className='flex items-center gap-2'>
                    <Clock className='h-4 w-4' />
                    {article.readTime}
                  </div>
                </div>

                <div className='flex items-center gap-4'>
                  <div className='flex items-center gap-1'>
                    <Eye className='h-4 w-4' />
                    {article.views.toLocaleString()}
                  </div>
                  <div className='flex items-center gap-1'>
                    <Star className='h-4 w-4' />
                    {likeCount}
                  </div>
                </div>
              </div>

              {/* アクションボタン */}
              <div className='flex items-center gap-4 mb-6'>
                <Button
                  variant={isLiked ? 'default' : 'outline'}
                  onClick={handleLike}
                  className='flex items-center gap-2'
                >
                  <Star
                    className={`h-4 w-4 ${isLiked ? 'fill-current' : ''}`}
                  />
                  {isLiked ? 'いいね済み' : 'いいね'}
                </Button>
                <Button
                  variant={isBookmarked ? 'default' : 'outline'}
                  onClick={handleBookmark}
                  className='flex items-center gap-2'
                >
                  <Bookmark
                    className={`h-4 w-4 ${isBookmarked ? 'fill-current' : ''}`}
                  />
                  {isBookmarked ? '保存済み' : '保存'}
                </Button>
                <Button
                  variant='outline'
                  onClick={handleShare}
                  className='flex items-center gap-2'
                >
                  <Share2 className='h-4 w-4' />
                  シェア
                </Button>
              </div>

              {/* タグ */}
              <div className='flex flex-wrap gap-2 mb-8'>
                {article.tags.map(tag => (
                  <Badge key={tag} variant='outline' className='text-sm'>
                    <Tag className='h-3 w-3 mr-1' />
                    {tag}
                  </Badge>
                ))}
              </div>
            </header>

            {/* 記事本文 */}
            <div className='prose prose-lg max-w-none'>
              <div
                className='whitespace-pre-wrap'
                dangerouslySetInnerHTML={{
                  __html: article.content
                    .replace(
                      /```(\w+)?\n([\s\S]*?)```/g,
                      '<pre><code class="language-$1">$2</code></pre>'
                    )
                    .replace(/`([^`]+)`/g, '<code>$1</code>')
                    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
                    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
                    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
                    .replace(/^\- (.*$)/gm, '<li>$1</li>')
                    .replace(/^\d+\. (.*$)/gm, '<li>$1</li>'),
                }}
              />
            </div>
          </article>

          {/* サイドバー */}
          <aside className='lg:col-span-1'>
            <div className='sticky top-8 space-y-6'>
              {/* 関連記事 */}
              <div>
                <h3 className='text-lg font-semibold mb-4'>関連記事</h3>
                <div className='space-y-4'>
                  {relatedArticles.map(article => (
                    <Link
                      key={article.id}
                      href={`/articles/${article.id}`}
                      className='block p-4 border rounded-lg hover:bg-muted transition-colors'
                    >
                      <div className='flex items-center gap-2 mb-2'>
                        {getCategoryBadge(article.category)}
                      </div>
                      <h4 className='font-medium text-sm line-clamp-2 mb-2'>
                        {article.title}
                      </h4>
                      <div className='flex items-center gap-3 text-xs text-muted-foreground'>
                        <div className='flex items-center gap-1'>
                          <Calendar className='h-3 w-3' />
                          {article.publishedAt}
                        </div>
                        <div className='flex items-center gap-1'>
                          <Clock className='h-3 w-3' />
                          {article.readTime}
                        </div>
                        <div className='flex items-center gap-1'>
                          <Eye className='h-3 w-3' />
                          {article.views}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>

              {/* 目次 */}
              <div>
                <h3 className='text-lg font-semibold mb-4'>目次</h3>
                <nav className='space-y-2'>
                  <a
                    href='#新機能'
                    className='block text-sm text-muted-foreground hover:text-foreground'
                  >
                    主な新機能
                  </a>
                  <a
                    href='#ベストプラクティス'
                    className='block text-sm text-muted-foreground hover:text-foreground'
                  >
                    ベストプラクティス
                  </a>
                  <a
                    href='#まとめ'
                    className='block text-sm text-muted-foreground hover:text-foreground'
                  >
                    まとめ
                  </a>
                </nav>
              </div>
            </div>
          </aside>
        </div>
      </main>

      <Footer />
    </div>
  );
}
