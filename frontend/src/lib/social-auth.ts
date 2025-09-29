import { signIn, signOut, getSession } from 'next-auth/react';
import { useAnalytics } from '@/lib/analytics';

export interface SocialProvider {
  id: string;
  name: string;
  icon: string;
  color: string;
  enabled: boolean;
}

export interface SocialProfile {
  provider: string;
  id: string;
  email: string;
  name: string;
  image?: string;
  username?: string;
  verified?: boolean;
  connectedAt: Date;
}

export interface SocialPost {
  id: string;
  provider: string;
  content: string;
  image?: string;
  url?: string;
  scheduledAt?: Date;
  publishedAt?: Date;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  engagement?: {
    likes?: number;
    shares?: number;
    comments?: number;
  };
}

class SocialAuthService {
  private analytics = useAnalytics();

  readonly providers: SocialProvider[] = [
    {
      id: 'google',
      name: 'Google',
      icon: 'google',
      color: '#4285F4',
      enabled: true,
    },
    {
      id: 'twitter',
      name: 'Twitter',
      icon: 'twitter',
      color: '#1DA1F2',
      enabled: false, // 実装が必要
    },
    {
      id: 'github',
      name: 'GitHub',
      icon: 'github',
      color: '#333333',
      enabled: false, // 実装が必要
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: 'linkedin',
      color: '#0077B5',
      enabled: false, // 実装が必要
    },
  ];

  /**
   * ソーシャルプロバイダーでサインイン
   */
  async signInWithProvider(providerId: string, redirectTo?: string): Promise<void> {
    try {
      this.analytics.track('Social Sign In Attempt', {
        provider: providerId,
        redirectTo,
      });

      const result = await signIn(providerId, {
        redirect: false,
        callbackUrl: redirectTo || '/dashboard',
      });

      if (result?.error) {
        throw new Error(result.error);
      }

      this.analytics.track('Social Sign In Success', {
        provider: providerId,
      });
    } catch (error) {
      this.analytics.track('Social Sign In Error', {
        provider: providerId,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw error;
    }
  }

  /**
   * サインアウト
   */
  async signOut(): Promise<void> {
    try {
      this.analytics.track('Sign Out', {});

      await signOut({
        redirect: false,
        callbackUrl: '/',
      });
    } catch (error) {
      this.analytics.track('Sign Out Error', {
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw error;
    }
  }

  /**
   * 現在のセッションを取得
   */
  async getCurrentSession() {
    return await getSession();
  }

  /**
   * ソーシャルプロファイルを取得
   */
  async getSocialProfiles(): Promise<SocialProfile[]> {
    try {
      const session = await this.getCurrentSession();
      if (!session?.user) {
        return [];
      }

      const profiles: SocialProfile[] = [];

      // Googleプロファイル
      if (session.user.email) {
        profiles.push({
          provider: 'google',
          id: session.user.email,
          email: session.user.email,
          name: session.user.name || '',
          image: session.user.image,
          verified: true,
          connectedAt: new Date(),
        });
      }

      return profiles;
    } catch (error) {
      console.error('Error getting social profiles:', error);
      return [];
    }
  }

  /**
   * ソーシャルプロファイルを切断
   */
  async disconnectProvider(providerId: string): Promise<void> {
    try {
      this.analytics.track('Social Disconnect', {
        provider: providerId,
      });

      // 実際の実装では、バックエンドAPIを呼び出してプロファイルを切断
      // ここでは簡易的な実装
      console.log(`Disconnecting ${providerId} provider`);
    } catch (error) {
      this.analytics.track('Social Disconnect Error', {
        provider: providerId,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw error;
    }
  }

  /**
   * ソーシャル投稿をスケジュール
   */
  async schedulePost(post: Omit<SocialPost, 'id' | 'status'>): Promise<SocialPost> {
    try {
      this.analytics.track('Social Post Schedule', {
        provider: post.provider,
        scheduledAt: post.scheduledAt?.toISOString(),
      });

      // 実際の実装では、バックエンドAPIを呼び出して投稿をスケジュール
      const scheduledPost: SocialPost = {
        id: `post_${Date.now()}`,
        ...post,
        status: 'scheduled',
      };

      return scheduledPost;
    } catch (error) {
      this.analytics.track('Social Post Schedule Error', {
        provider: post.provider,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw error;
    }
  }

  /**
   * スケジュールされた投稿を取得
   */
  async getScheduledPosts(): Promise<SocialPost[]> {
    try {
      // 実際の実装では、バックエンドAPIから取得
      return [];
    } catch (error) {
      console.error('Error getting scheduled posts:', error);
      return [];
    }
  }

  /**
   * 投稿を削除
   */
  async deletePost(postId: string): Promise<void> {
    try {
      this.analytics.track('Social Post Delete', {
        postId,
      });

      // 実際の実装では、バックエンドAPIを呼び出して投稿を削除
      console.log(`Deleting post ${postId}`);
    } catch (error) {
      this.analytics.track('Social Post Delete Error', {
        postId,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
      throw error;
    }
  }

  /**
   * ソーシャルエンゲージメントを取得
   */
  async getEngagement(postId: string): Promise<SocialPost['engagement']> {
    try {
      // 実際の実装では、各プラットフォームのAPIから取得
      return {
        likes: Math.floor(Math.random() * 100),
        shares: Math.floor(Math.random() * 50),
        comments: Math.floor(Math.random() * 30),
      };
    } catch (error) {
      console.error('Error getting engagement:', error);
      return {};
    }
  }

  /**
   * 利用可能なプロバイダーを取得
   */
  getAvailableProviders(): SocialProvider[] {
    return this.providers.filter(provider => provider.enabled);
  }

  /**
   * プロバイダーが有効かチェック
   */
  isProviderEnabled(providerId: string): boolean {
    const provider = this.providers.find(p => p.id === providerId);
    return provider?.enabled || false;
  }
}

// グローバルインスタンス
const socialAuthService = new SocialAuthService();

/**
 * ソーシャル認証用のReactフック
 */
export function useSocialAuth() {
  const signInWithProvider = async (providerId: string, redirectTo?: string) => {
    return await socialAuthService.signInWithProvider(providerId, redirectTo);
  };

  const signOut = async () => {
    return await socialAuthService.signOut();
  };

  const getCurrentSession = async () => {
    return await socialAuthService.getCurrentSession();
  };

  const getSocialProfiles = async () => {
    return await socialAuthService.getSocialProfiles();
  };

  const disconnectProvider = async (providerId: string) => {
    return await socialAuthService.disconnectProvider(providerId);
  };

  const schedulePost = async (post: Omit<SocialPost, 'id' | 'status'>) => {
    return await socialAuthService.schedulePost(post);
  };

  const getScheduledPosts = async () => {
    return await socialAuthService.getScheduledPosts();
  };

  const deletePost = async (postId: string) => {
    return await socialAuthService.deletePost(postId);
  };

  const getEngagement = async (postId: string) => {
    return await socialAuthService.getEngagement(postId);
  };

  const getAvailableProviders = () => {
    return socialAuthService.getAvailableProviders();
  };

  const isProviderEnabled = (providerId: string) => {
    return socialAuthService.isProviderEnabled(providerId);
  };

  return {
    signInWithProvider,
    signOut,
    getCurrentSession,
    getSocialProfiles,
    disconnectProvider,
    schedulePost,
    getScheduledPosts,
    deletePost,
    getEngagement,
    getAvailableProviders,
    isProviderEnabled,
  };
}

export default socialAuthService;
