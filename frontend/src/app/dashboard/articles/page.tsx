'use client';

import { Footer } from '@/components/footer';
import { Header } from '@/components/header';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Search,
  Filter,
  Plus,
  Edit,
  Trash2,
  Eye,
  Calendar,
  TrendingUp,
  Star,
} from 'lucide-react';
import { useState } from 'react';

export default function ArticlesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  // モックデータ（実際の実装ではAPIから取得）
  const articles = [
    {
      id: 1,
      title: 'TypeScript 5.0の新機能とベストプラクティス',
      status: 'published',
      views: 1234,
      likes: 89,
      publishedAt: '2024-09-08',
      tags: ['TypeScript', 'JavaScript', 'Tutorial'],
    },
    {
      id: 2,
      title: 'Next.js 14 App Router完全ガイド',
      status: 'draft',
      views: 0,
      likes: 0,
      publishedAt: null,
      tags: ['Next.js', 'React', 'Tutorial'],
    },
    {
      id: 3,
      title: 'React Server Componentsの実践的活用法',
      status: 'published',
      views: 756,
      likes: 45,
      publishedAt: '2024-09-06',
      tags: ['React', 'Server Components', 'Performance'],
    },
    {
      id: 4,
      title: 'TypeScript型安全性の向上テクニック',
      status: 'scheduled',
      views: 0,
      likes: 0,
      publishedAt: '2024-09-15',
      tags: ['TypeScript', 'Type Safety', 'Best Practices'],
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return <Badge className='bg-green-100 text-green-800'>公開中</Badge>;
      case 'draft':
        return <Badge variant='secondary'>下書き</Badge>;
      case 'scheduled':
        return <Badge className='bg-blue-100 text-blue-800'>予約投稿</Badge>;
      default:
        return <Badge variant='outline'>{status}</Badge>;
    }
  };

  const filteredArticles = articles.filter(article => {
    const matchesSearch = article.title
      .toLowerCase()
      .includes(searchQuery.toLowerCase());
    const matchesFilter =
      filterStatus === 'all' || article.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className='min-h-screen bg-background'>
      <Header />
      
      <main className='container py-8'>
        <div className='mb-8'>
          <div className='flex items-center justify-between'>
            <div>
              <h1 className='text-3xl font-bold text-foreground'>記事管理</h1>
              <p className='text-muted-foreground mt-2'>
                作成した記事を管理・編集できます
              </p>
            </div>
            <Button>
              <Plus className='mr-2 h-4 w-4' />
              新しい記事
            </Button>
          </div>
        </div>

        {/* 検索・フィルター */}
        <Card className='mb-6'>
          <CardContent className='pt-6'>
            <div className='flex flex-col sm:flex-row gap-4'>
              <div className='relative flex-1'>
                <Search className='absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground' />
                <Input
                  placeholder='記事を検索...'
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className='pl-10'
                />
              </div>
              <div className='flex gap-2'>
                <Button
                  variant={filterStatus === 'all' ? 'default' : 'outline'}
                  onClick={() => setFilterStatus('all')}
                >
                  すべて
                </Button>
                <Button
                  variant={filterStatus === 'published' ? 'default' : 'outline'}
                  onClick={() => setFilterStatus('published')}
                >
                  公開中
                </Button>
                <Button
                  variant={filterStatus === 'draft' ? 'default' : 'outline'}
                  onClick={() => setFilterStatus('draft')}
                >
                  下書き
                </Button>
                <Button
                  variant={filterStatus === 'scheduled' ? 'default' : 'outline'}
                  onClick={() => setFilterStatus('scheduled')}
                >
                  予約投稿
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 記事一覧 */}
        <div className='space-y-4'>
          {filteredArticles.map(article => (
            <Card key={article.id}>
              <CardContent className='pt-6'>
                <div className='flex items-start justify-between'>
                  <div className='flex-1'>
                    <div className='flex items-center gap-3 mb-2'>
                      <h3 className='text-lg font-semibold'>{article.title}</h3>
                      {getStatusBadge(article.status)}
                    </div>
                    
                    <div className='flex items-center gap-4 text-sm text-muted-foreground mb-3'>
                      <div className='flex items-center gap-1'>
                        <Calendar className='h-4 w-4' />
                        {article.publishedAt || '未公開'}
                      </div>
                      <div className='flex items-center gap-1'>
                        <Eye className='h-4 w-4' />
                        {article.views} 回閲覧
                      </div>
                      <div className='flex items-center gap-1'>
                        <Star className='h-4 w-4' />
                        {article.likes} いいね
                      </div>
                    </div>

                    <div className='flex flex-wrap gap-2'>
                      {article.tags.map(tag => (
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
                    <Button variant='outline' size='sm' className='text-destructive'>
                      <Trash2 className='h-4 w-4' />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredArticles.length === 0 && (
          <Card>
            <CardContent className='pt-6 text-center'>
              <p className='text-muted-foreground'>
                {searchQuery || filterStatus !== 'all'
                  ? '条件に一致する記事が見つかりませんでした'
                  : 'まだ記事がありません'}
              </p>
              <Button className='mt-4'>
                <Plus className='mr-2 h-4 w-4' />
                最初の記事を作成
              </Button>
            </CardContent>
          </Card>
        )}
      </main>

      <Footer />
    </div>
  );
}
