'use client';

import { Button } from '@/components/ui/button';
import { Menu, User, X } from 'lucide-react';
import { signIn, signOut, useSession } from 'next-auth/react';
import Link from 'next/link';
import { useState } from 'react';

export function Header() {
  const { data: session, status } = useSession();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className='sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60'>
      <div className='container flex h-16 items-center justify-between'>
        <div className='flex items-center space-x-4'>
          <Link href='/' className='flex items-center space-x-2'>
            <div className='h-8 w-8 rounded bg-primary'></div>
            <span className='text-xl font-bold'>AICA-SyS</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className='hidden md:flex items-center space-x-6'>
          <Link
            href='/articles'
            className='text-sm font-medium hover:text-primary'
          >
            記事
          </Link>
          <Link
            href='/newsletters'
            className='text-sm font-medium hover:text-primary'
          >
            ニュースレター
          </Link>
          <Link
            href='/trends'
            className='text-sm font-medium hover:text-primary'
          >
            トレンド
          </Link>
          <Link
            href='/pricing'
            className='text-sm font-medium hover:text-primary'
          >
            料金
          </Link>
        </nav>

        {/* Desktop Auth */}
        <div className='hidden md:flex items-center space-x-4'>
          {status === 'loading' ? (
            <div className='h-9 w-20 animate-pulse rounded bg-muted'></div>
          ) : session ? (
            <div className='flex items-center space-x-4'>
              <Link href='/dashboard'>
                <Button variant='outline' size='sm'>
                  <User className='h-4 w-4 mr-2' />
                  ダッシュボード
                </Button>
              </Link>
              <Button variant='outline' size='sm' onClick={() => signOut()}>
                ログアウト
              </Button>
            </div>
          ) : (
            <div className='flex items-center space-x-2'>
              <Button
                variant='outline'
                size='sm'
                onClick={() => signIn('google')}
              >
                ログイン
              </Button>
              <Link href='/auth/signup'>
                <Button size='sm'>無料で始める</Button>
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          className='md:hidden'
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? (
            <X className='h-6 w-6' />
          ) : (
            <Menu className='h-6 w-6' />
          )}
        </button>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className='md:hidden border-t bg-background'>
          <div className='container py-4 space-y-4'>
            <nav className='flex flex-col space-y-4'>
              <Link
                href='/articles'
                className='text-sm font-medium hover:text-primary'
              >
                記事
              </Link>
              <Link
                href='/newsletters'
                className='text-sm font-medium hover:text-primary'
              >
                ニュースレター
              </Link>
              <Link
                href='/trends'
                className='text-sm font-medium hover:text-primary'
              >
                トレンド
              </Link>
              <Link
                href='/pricing'
                className='text-sm font-medium hover:text-primary'
              >
                料金
              </Link>
            </nav>
            <div className='pt-4 border-t'>
              {session ? (
                <div className='flex flex-col space-y-2'>
                  <Link href='/dashboard'>
                    <Button variant='outline' size='sm' className='w-full'>
                      <User className='h-4 w-4 mr-2' />
                      ダッシュボード
                    </Button>
                  </Link>
                  <Button
                    variant='outline'
                    size='sm'
                    onClick={() => signOut()}
                    className='w-full'
                  >
                    ログアウト
                  </Button>
                </div>
              ) : (
                <div className='flex flex-col space-y-2'>
                  <Button
                    variant='outline'
                    size='sm'
                    onClick={() => signIn('google')}
                    className='w-full'
                  >
                    ログイン
                  </Button>
                  <Button size='sm' className='w-full'>
                    無料で始める
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
