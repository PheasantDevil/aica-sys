'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  FileText,
  Mail,
  BarChart3,
  CreditCard,
  User,
  Settings,
} from 'lucide-react';

const navigation = [
  {
    name: 'ダッシュボード',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: '記事管理',
    href: '/dashboard/articles',
    icon: FileText,
  },
  {
    name: 'ニュースレター',
    href: '/dashboard/newsletters',
    icon: Mail,
  },
  {
    name: '分析レポート',
    href: '/dashboard/analytics',
    icon: BarChart3,
  },
  {
    name: 'サブスクリプション',
    href: '/dashboard/subscription',
    icon: CreditCard,
  },
  {
    name: 'プロフィール',
    href: '/dashboard/profile',
    icon: User,
  },
];

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col space-y-2">
      {navigation.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
              isActive
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted hover:text-foreground'
            )}
          >
            <item.icon className="h-4 w-4" />
            <span>{item.name}</span>
          </Link>
        );
      })}
    </nav>
  );
}
