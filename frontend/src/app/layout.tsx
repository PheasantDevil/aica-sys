import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ErrorProvider } from '@/components/ErrorProvider';
import PerformanceMonitor from '@/components/PerformanceMonitor';
import { PerformanceProvider } from '@/components/PerformanceProvider';
import { Providers } from '@/components/providers';
import { SpeedInsights } from '@vercel/speed-insights/next';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

// Optimize font loading
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  preload: true,
  fallback: ['system-ui', 'arial'],
});

export const metadata: Metadata = {
  title: 'AICA-SyS - AI-driven Information Curation System',
  description:
    'AI-driven niche information curation and automated sales system',
  keywords: ['AI', 'information curation', 'automated sales', 'niche markets'],
  authors: [{ name: 'AICA-SyS Team' }],
  creator: 'AICA-SyS',
  publisher: 'AICA-SyS',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(
    'https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app'
  ),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'AICA-SyS - AI-driven Information Curation System',
    description:
      'AI-driven niche information curation and automated sales system',
    url: 'https://aica-sys-konishib0engineer-gmailcoms-projects.vercel.app',
    siteName: 'AICA-SyS',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'AICA-SyS - AI-driven Information Curation System',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AICA-SyS - AI-driven Information Curation System',
    description:
      'AI-driven niche information curation and automated sales system',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='en'>
      <head>
        <link rel='icon' href='/favicon.ico' />
        <link rel='apple-touch-icon' href='/apple-touch-icon.png' />
        <link rel='manifest' href='/manifest.json' />
        <meta name='theme-color' content='#000000' />
        <meta name='viewport' content='width=device-width, initial-scale=1' />
      </head>
      <body className={inter.className}>
        <Providers>
          <ErrorProvider>
            <PerformanceProvider>
              <ErrorBoundary>
                {children}
                <PerformanceMonitor
                  enabled={process.env.NODE_ENV === 'production'}
                />
              </ErrorBoundary>
            </PerformanceProvider>
          </ErrorProvider>
        </Providers>
        <SpeedInsights />
      </body>
    </html>
  );
}
