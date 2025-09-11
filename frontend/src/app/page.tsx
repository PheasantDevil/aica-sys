import { Features } from '@/components/features';
import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import { Hero } from '@/components/hero';
import { Pricing } from '@/components/pricing';
import { SEOUtils } from '@/lib/seo';
import { Metadata } from 'next';

export const metadata: Metadata = SEOUtils.generateMetadata({
  title: 'AICA-SyS - AI駆動型TypeScriptエコシステム特化型プラットフォーム',
  description:
    'TypeScriptエコシステム特化型のAI自動コンテンツ生成・販売システム。最新の技術情報、チュートリアル、トレンド分析を提供します。',
  keywords: [
    'TypeScript',
    'AI',
    '自動コンテンツ生成',
    'プログラミング',
    '開発ツール',
    '技術情報',
    'キュレーション',
    'サブスクリプション',
    'Next.js',
    'React',
    'Node.js',
  ],
  canonical: '/',
  ogType: 'website',
  structuredData: SEOUtils.generateStructuredData('website', {}),
});

export default function HomePage() {
  return (
    <div className='min-h-screen bg-background'>
      <Header />
      <main>
        <Hero />
        <Features />
        <Pricing />
      </main>
      <Footer />
    </div>
  );
}
