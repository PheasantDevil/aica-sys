'use client';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

function AuthErrorContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get('error');

  const getErrorMessage = (error: string | null) => {
    switch (error) {
      case 'Configuration':
        return '認証設定に問題があります。管理者にお問い合わせください。';
      case 'AccessDenied':
        return 'アクセスが拒否されました。';
      case 'Verification':
        return '認証トークンが無効または期限切れです。';
      default:
        return '認証中にエラーが発生しました。もう一度お試しください。';
    }
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-background'>
      <Card className='w-full max-w-md'>
        <CardHeader className='text-center'>
          <div className='mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10'>
            <AlertCircle className='h-6 w-6 text-destructive' />
          </div>
          <CardTitle className='text-2xl'>認証エラー</CardTitle>
          <CardDescription>{getErrorMessage(error)}</CardDescription>
        </CardHeader>
        <CardContent className='space-y-4'>
          <div className='flex flex-col space-y-2'>
            <Button asChild>
              <Link href='/auth/signin'>もう一度ログイン</Link>
            </Button>
            <Button variant='outline' asChild>
              <Link href='/'>ホームに戻る</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AuthErrorContent />
    </Suspense>
  );
}
