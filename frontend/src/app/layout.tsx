import { ErrorBoundary } from "@/components/ErrorBoundary";
import { ErrorProvider } from "@/components/ErrorProvider";
import PerformanceMonitor from "@/components/PerformanceMonitor";
import { PerformanceProvider } from "@/components/PerformanceProvider";
import { Providers } from "@/components/providers";
import { GoogleAnalytics } from "@next/third-parties/google";
import { SpeedInsights } from "@vercel/speed-insights/next";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// Optimize font loading
const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  preload: true,
  fallback: ["system-ui", "arial"],
});

const SITE_URL = process.env.NEXT_PUBLIC_BASE_URL || "https://aica-sys.vercel.app";
const GOOGLE_SITE_VERIFICATION = process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION;
const GA_MEASUREMENT_ID = process.env.NEXT_PUBLIC_GA_ID;
const DEFAULT_DESCRIPTION =
  "TypeScriptエコシステム特化型のAI自動コンテンツ生成・販売システム。最新トレンド、技術記事、ニュースレターを自動配信。";
const DEFAULT_KEYWORDS = [
  "TypeScript",
  "AI",
  "自動コンテンツ生成",
  "プログラミング",
  "開発ツール",
  "技術情報",
  "キュレーション",
  "サブスクリプション",
  "Next.js",
  "FastAPI",
];

const defaultOgImageParams = new URLSearchParams({
  title: "AICA-SyS - AI-driven TypeScript Content & Sales System",
  description: DEFAULT_DESCRIPTION,
  theme: "dark",
});
const DEFAULT_OG_IMAGE = `${SITE_URL}/api/og?${defaultOgImageParams.toString()}`;

export const metadata: Metadata = {
  title: {
    default: "AICA-SyS - AI-driven TypeScript Content & Sales System",
    template: "%s | AICA-SyS",
  },
  description: DEFAULT_DESCRIPTION,
  keywords: DEFAULT_KEYWORDS,
  authors: [{ name: "AICA-SyS Team" }],
  creator: "AICA-SyS",
  publisher: "AICA-SyS",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(SITE_URL),
  alternates: {
    canonical: SITE_URL,
  },
  openGraph: {
    title: "AICA-SyS - AI-driven TypeScript Content & Sales System",
    description: DEFAULT_DESCRIPTION,
    url: SITE_URL,
    siteName: "AICA-SyS",
    images: [
      {
        url: DEFAULT_OG_IMAGE,
        width: 1200,
        height: 630,
        alt: "AICA-SyS - AI-driven TypeScript Content & Sales System",
      },
    ],
    locale: "ja_JP",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AICA-SyS - AI-driven TypeScript Content & Sales System",
    description: DEFAULT_DESCRIPTION,
    images: [DEFAULT_OG_IMAGE],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: GOOGLE_SITE_VERIFICATION
    ? {
        google: GOOGLE_SITE_VERIFICATION,
      }
    : undefined,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#000000" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className={inter.className}>
        <Providers>
          <ErrorProvider>
            <PerformanceProvider>
              <ErrorBoundary>
                {children}
                <PerformanceMonitor enabled={process.env.NODE_ENV === "production"} />
              </ErrorBoundary>
            </PerformanceProvider>
          </ErrorProvider>
        </Providers>
        <SpeedInsights />
        {GA_MEASUREMENT_ID ? <GoogleAnalytics gaId={GA_MEASUREMENT_ID} /> : null}
      </body>
    </html>
  );
}
