'use client';

import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
  className?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
};

export function Loading({ size = 'md', text, className }: LoadingProps) {
  return (
    <div className={cn('flex items-center justify-center gap-2', className)}>
      <Loader2 className={cn('animate-spin', sizeClasses[size])} />
      {text && <span className='text-sm text-muted-foreground'>{text}</span>}
    </div>
  );
}

export function LoadingCard({ className }: { className?: string }) {
  return (
    <div className={cn('p-6 space-y-4', className)}>
      <div className='space-y-2'>
        <div className='h-4 bg-muted rounded animate-pulse'></div>
        <div className='h-3 bg-muted rounded animate-pulse w-2/3'></div>
      </div>
      <div className='space-y-2'>
        <div className='h-3 bg-muted rounded animate-pulse'></div>
        <div className='h-3 bg-muted rounded animate-pulse'></div>
        <div className='h-3 bg-muted rounded animate-pulse w-1/2'></div>
      </div>
    </div>
  );
}

export function LoadingGrid({
  count = 6,
  className,
}: {
  count?: number;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6',
        className
      )}
    >
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className='h-64 animate-pulse bg-muted rounded-lg'></div>
      ))}
    </div>
  );
}
