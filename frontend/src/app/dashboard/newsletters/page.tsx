'use client';

import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Calendar,
  Edit,
  Eye,
  Mail,
  Plus,
  Search,
  Send,
  Trash2,
  Users,
} from 'lucide-react';
import { useState } from 'react';

export default function NewslettersPage() {
  const [searchQuery, setSearchQuery] = useState('');

  // モックデータ（実際の実装ではAPIから取得）
  const newsletters = [
    {
      id: 1,
      title: 'TypeScript週間レポート #42',
      status: 'sent',
      subscribers: 1234,
      openRate: 68.5,
      clickRate: 12.3,
      sentAt: '2024-09-08',
      tags: ['Weekly', 'TypeScript', 'Report'],
    },
    {
      id: 2,
      title: 'Next.js 14新機能まとめ',
      status: 'draft',
      subscribers: 0,
      openRate: 0,
      clickRate: 0,
      sentAt: null,
      tags: ['Next.js', 'React', 'Features'],
    },
    {
      id: 3,
      title: 'React Server Components完全ガイド',
      status: 'scheduled',
      subscribers: 1234,
      openRate: 0,
      clickRate: 0,
      sentAt: '2024-09-15',
      tags: ['React', 'Server Components', 'Tutorial'],
    },
    {
      id: 4,
      title: 'TypeScript型安全性のベストプラクティス',
      status: 'sent',
      subscribers: 1234,
      openRate: 72.1,
      clickRate: 15.8,
      sentAt: '2024-09-01',
      tags: ['TypeScript', 'Best Practices', 'Type Safety'],
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'sent':
        return <Badge className='bg-green-100 text-green-800'>送信済み</Badge>;
      case 'draft':
        return <Badge variant='secondary'>下書き</Badge>;
      case 'scheduled':
        return <Badge className='bg-blue-100 text-blue-800'>予約送信</Badge>;
      default:
        return <Badge variant='outline'>{status}</Badge>;
    }
  };

  const filteredNewsletters = newsletters.filter(newsletter =>
    newsletter.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className='min-h-screen bg-background'>
      <Header />

      <main className='container py-8'>
        <div className='mb-8'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>
                ニュースレター管理
              </h1>
              <p className='text-muted-foreground mt-2'>
                ニュースレターの作成・送信・分析ができます
              </p>
            </div>
            <Button>
              <Plus className='mr-2 h-4 w-4' />
              新しいニュースレター
            </Button>
          </div>
        </div>

        {/* 統計カード */}
        <div className='grid grid-cols-1 md:grid-cols-4 gap-6 mb-8'>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    総購読者数
                  </p>
                  <p className='text-2xl font-bold'>1,234</p>
                </div>
                <Users className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    平均開封率
                  </p>
                  <p className='text-2xl font-bold'>68.5%</p>
                </div>
                <Eye className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    平均クリック率
                  </p>
                  <p className='text-2xl font-bold'>12.3%</p>
                </div>
                <Mail className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center justify-between'>
                <div>
                  <p className='text-sm font-medium text-muted-foreground'>
                    今月の送信数
                  </p>
                  <p className='text-2xl font-bold'>4</p>
                </div>
                <Send className='h-8 w-8 text-muted-foreground' />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 検索 */}
        <Card className='mb-6'>
          <CardContent className='pt-6'>
            <div className='relative'>
              <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
              <Input
                placeholder='ニュースレターを検索...'
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className='pl-10'
              />
            </div>
          </CardContent>
        </Card>

        {/* ニュースレター一覧 */}
        <div className='space-y-4'>
          {filteredNewsletters.map(newsletter => (
            <Card key={newsletter.id}>
              <CardContent className='pt-6'>
                <div className='flex items-start justify-between'>
                  <div className='flex-1'>
                    <div className='flex items-center gap-3 mb-2'>
                      <h3 className='text-lg font-semibold'>
                        {newsletter.title}
                      </h3>
                      {getStatusBadge(newsletter.status)}
                    </div>

                    <div className='grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-muted-foreground mb-3'>
                      <div className='flex items-center gap-1'>
                        <Users className='h-4 w-4' />
                        {newsletter.subscribers.toLocaleString()} 購読者
                      </div>
                      <div className='flex items-center gap-1'>
                        <Eye className='h-4 w-4' />
                        {newsletter.openRate}% 開封率
                      </div>
                      <div className='flex items-center gap-1'>
                        <Mail className='h-4 w-4' />
                        {newsletter.clickRate}% クリック率
                      </div>
                      <div className='flex items-center gap-1'>
                        <Calendar className='h-4 w-4' />
                        {newsletter.sentAt || '未送信'}
                      </div>
                    </div>

                    <div className='flex flex-wrap gap-2'>
                      {newsletter.tags.map(tag => (
                        <Badge key={tag} variant='outline' className='text-xs'>
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className='flex items-center gap-2 ml-4'>
                    <Button variant='outline' size='sm'>
                      <Edit className='h-4 w-4' />
                    </Button>
                    <Button variant='outline' size='sm'>
                      <Eye className='h-4 w-4' />
                    </Button>
                    {newsletter.status === 'draft' && (
                      <Button variant='outline' size='sm'>
                        <Send className='h-4 w-4' />
                      </Button>
                    )}
                    <Button
                      variant='outline'
                      size='sm'
                      className='text-destructive'
                    >
                      <Trash2 className='h-4 w-4' />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredNewsletters.length === 0 && (
          <Card>
            <CardContent className='pt-6 text-center'>
              <p className='text-muted-foreground'>
                {searchQuery
                  ? '条件に一致するニュースレターが見つかりませんでした'
                  : 'まだニュースレターがありません'}
              </p>
              <Button className='mt-4'>
                <Plus className='mr-2 h-4 w-4' />
                最初のニュースレターを作成
              </Button>
            </CardContent>
          </Card>
        )}
      </main>

      <Footer />
    </div>
  );
}
