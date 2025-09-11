'use client';

import { Header } from '@/components/header';
import { Footer } from '@/components/footer';
import { SettingsNavigation } from '@/components/settings/settings-navigation';
import { ProfileSettings } from '@/components/settings/profile-settings';
import { AccountSettings } from '@/components/settings/account-settings';
import { NotificationSettings } from '@/components/settings/notification-settings';
import { SecuritySettings } from '@/components/settings/security-settings';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';

type SettingsTab = 'profile' | 'account' | 'notifications' | 'security';

export default function SettingsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/auth/signin?callbackUrl=/settings');
      return;
    }
    setIsLoading(false);
  }, [session, status, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container py-20">
          <div className="flex items-center justify-center">
            <div className="flex items-center gap-2">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span>読み込み中...</span>
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'profile':
        return <ProfileSettings />;
      case 'account':
        return <AccountSettings />;
      case 'notifications':
        return <NotificationSettings />;
      case 'security':
        return <SecuritySettings />;
      default:
        return <ProfileSettings />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">設定</h1>
            <p className="text-muted-foreground">
              アカウント設定と個人情報を管理できます
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="lg:col-span-1">
              <SettingsNavigation 
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
            </div>
            
            <div className="lg:col-span-3">
              {renderActiveTab()}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
