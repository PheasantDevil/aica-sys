import { AnalyticsButton } from "@/components/analytics/analytics-button";
import { ArticleViewTracker } from "@/components/content/article-view-tracker";
import { RecommendedArticles } from "@/components/content/recommended-articles";
import { SEOUtils } from "@/lib/seo";
import { Metadata } from "next";
import { notFound } from "next/navigation";

interface ArticlePageProps {
  params: {
    slug: string;
  };
}

// Mock data - in production, fetch from API
async function getArticle(slug: string) {
  // This would be an API call in production
  const articles = [
    {
      id: "1",
      slug: "typescript-best-practices-2024",
      title: "TypeScript ベストプラクティス 2024年版",
      description: "2024年に向けたTypeScriptの最新ベストプラクティスとパターンを詳しく解説します。",
      content: "TypeScriptの最新機能とベストプラクティスについて...",
      author: {
        name: "AICA-SyS",
        avatar: "/authors/aica-sys.jpg",
      },
      category: "tutorial",
      tags: ["TypeScript", "JavaScript", "開発", "ベストプラクティス"],
      publishedAt: "2024-01-15T10:00:00Z",
      readTime: 8,
      views: 1250,
      likes: 45,
      isPremium: false,
      imageUrl: "/articles/typescript-best-practices.jpg",
    },
  ];

  return articles.find((article) => article.slug === slug) || null;
}

export async function generateMetadata({ params }: ArticlePageProps): Promise<Metadata> {
  const article = await getArticle(params.slug);

  if (!article) {
    return {
      title: "記事が見つかりません",
      description: "お探しの記事が見つかりませんでした。",
    };
  }

  const keywords = SEOUtils.extractKeywords(
    `${article.title} ${article.description} ${article.tags.join(" ")}`,
  );

  return SEOUtils.generateMetadata({
    title: article.title,
    description: article.description,
    keywords,
    canonical: `/articles/${article.slug}`,
    ogImage: SEOUtils.generateOGImageUrl(article.title, article.description),
    ogType: "article",
    structuredData: SEOUtils.generateStructuredData("article", {
      title: article.title,
      description: article.description,
      image: article.imageUrl,
      author: article.author.name,
      publishedAt: article.publishedAt,
      updatedAt: article.publishedAt,
      url: `/articles/${article.slug}`,
    }),
  });
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const article = await getArticle(params.slug);

  if (!article) {
    notFound();
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Article Header */}
      <header className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {article.category}
          </span>
          <span className="text-sm text-gray-500">
            {new Date(article.publishedAt).toLocaleDateString("ja-JP")}
          </span>
          <span className="text-sm text-gray-500">{article.readTime}分で読める</span>
        </div>

        <h1 className="text-4xl font-bold text-gray-900 mb-4">{article.title}</h1>

        <p className="text-xl text-gray-600 mb-6">{article.description}</p>

        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <img
              src={article.author.avatar}
              alt={article.author.name}
              className="w-10 h-10 rounded-full"
            />
            <span className="text-gray-700">{article.author.name}</span>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span>{article.views} 回閲覧</span>
            <span>{article.likes} いいね</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {article.tags.map((tag) => (
            <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
              #{tag}
            </span>
          ))}
        </div>
      </header>

      {/* Article Image */}
      <div className="mb-8">
        <img
          src={article.imageUrl}
          alt={article.title}
          className="w-full h-64 object-cover rounded-lg"
        />
      </div>

      {/* Article Content */}
      <article className="prose prose-lg max-w-none mb-8">
        <div dangerouslySetInnerHTML={{ __html: article.content }} />
      </article>

      {/* View Tracker - 閲覧履歴を記録 */}
      <ArticleViewTracker
        articleId={article.id}
        metadata={{
          category: article.category,
          tags: article.tags,
          title: article.title,
        }}
      />

      {/* Article Actions */}
      <div className="flex items-center gap-4 mb-8">
        <AnalyticsButton
          eventName="article_like"
          eventParameters={{
            content_id: article.id,
            content_type: "article",
            content_title: article.title,
          }}
          variant="outline"
        >
          👍 いいね ({article.likes})
        </AnalyticsButton>

        <AnalyticsButton
          eventName="article_share"
          eventParameters={{
            content_id: article.id,
            content_type: "article",
            content_title: article.title,
          }}
          variant="outline"
        >
          📤 シェア
        </AnalyticsButton>

        <AnalyticsButton
          eventName="article_bookmark"
          eventParameters={{
            content_id: article.id,
            content_type: "article",
            content_title: article.title,
          }}
          variant="outline"
        >
          🔖 ブックマーク
        </AnalyticsButton>
      </div>

      {/* Similar Articles - 類似記事推薦 */}
      <RecommendedArticles contentId={article.id} type="similar" limit={6} title="関連記事" />
    </div>
  );
}
