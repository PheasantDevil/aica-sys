'use client';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { getSession, signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function SignInPage() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // 既にログインしている場合はダッシュボードにリダイレクト
    getSession().then(session => {
      if (session) {
        router.push('/dashboard');
      }
    });
  }, [router]);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      await signIn('google', { callbackUrl: '/dashboard' });
    } catch (error) {
      console.error('Sign in error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='min-h-screen flex items-center justify-center bg-background'>
      <Card className='w-full max-w-md'>
        <CardHeader className='text-center'>
          <CardTitle className='text-2xl'>ログイン</CardTitle>
          <CardDescription>
            AICA-SyS にログインして、TypeScriptの最新情報を取得しましょう
          </CardDescription>
        </CardHeader>
        <CardContent className='space-y-4'>
          <Button
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className='w-full'
            size='lg'
          >
            {isLoading ? 'ログイン中...' : 'Googleでログイン'}
          </Button>

          <div className='text-center text-sm text-muted-foreground'>
            ログインすることで、
            <a href='/terms' className='underline hover:text-primary'>
              利用規約
            </a>
            および
            <a href='/privacy' className='underline hover:text-primary'>
              プライバシーポリシー
            </a>
            に同意したものとみなされます。
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
