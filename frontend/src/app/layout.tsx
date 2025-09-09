import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from './providers'
import { PerformanceMonitor } from '@/components/performance-monitor'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AICA-SyS - AI-driven Content Curation & Automated Sales System',
  description: 'TypeScriptエコシステム特化型のAI自動コンテンツ生成・販売システム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <Providers>
          {children}
          <PerformanceMonitor />
        </Providers>
      </body>
    </html>
  )
}
