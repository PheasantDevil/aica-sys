import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { PerformanceMonitor } from '@/components/performance-monitor'
import { AnalyticsProvider, Analytics } from '@/components/analytics'
import { defaultSEO } from '@/lib/seo'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  ...defaultSEO,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <AnalyticsProvider>
          <Providers>
            {children}
            <PerformanceMonitor />
            <Analytics />
          </Providers>
        </AnalyticsProvider>
      </body>
    </html>
  )
}
