'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Shield, 
  Key, 
  Smartphone, 
  Globe, 
  CheckCircle, 
  AlertTriangle,
  Eye,
  EyeOff
} from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

export function SecuritySettings() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const handlePasswordChange = (field: string, value: string) => {
    setPasswordData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('新しいパスワードが一致しません');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      toast.error('パスワードは8文字以上である必要があります');
      return;
    }

    setIsLoading(true);
    
    try {
      // 実際の実装ではAPIを呼び出してパスワードを変更
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('パスワードが変更されました');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
    } catch (error) {
      console.error('Password change error:', error);
      toast.error('パスワードの変更に失敗しました');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTwoFactorToggle = () => {
    toast.info('二要素認証機能は準備中です');
  };

  const handleSessionRevoke = () => {
    toast.info('セッション管理機能は準備中です');
  };

  return (
    <div className="space-y-6">
      {/* パスワード変更 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            パスワード
          </CardTitle>
          <CardDescription>
            アカウントのセキュリティを保つために、定期的にパスワードを変更してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="currentPassword">現在のパスワード</Label>
              <div className="relative">
                <Input
                  id="currentPassword"
                  type={showPassword ? 'text' : 'password'}
                  value={passwordData.currentPassword}
                  onChange={(e) => handlePasswordChange('currentPassword', e.target.value)}
                  placeholder="現在のパスワードを入力"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="newPassword">新しいパスワード</Label>
              <Input
                id="newPassword"
                type="password"
                value={passwordData.newPassword}
                onChange={(e) => handlePasswordChange('newPassword', e.target.value)}
                placeholder="新しいパスワードを入力"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">新しいパスワード（確認）</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => handlePasswordChange('confirmPassword', e.target.value)}
                placeholder="新しいパスワードを再入力"
              />
            </div>

            <Button type="submit" disabled={isLoading}>
              {isLoading ? '変更中...' : 'パスワードを変更'}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* 二要素認証 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="h-5 w-5" />
            二要素認証
          </CardTitle>
          <CardDescription>
            アカウントのセキュリティを強化するために二要素認証を有効にしてください
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-muted rounded-lg">
                <Smartphone className="h-5 w-5" />
              </div>
              <div>
                <p className="font-medium">SMS認証</p>
                <p className="text-sm text-muted-foreground">
                  携帯電話番号に送信されるコードで認証
                </p>
              </div>
            </div>
            <Badge variant="outline">無効</Badge>
          </div>

          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-muted rounded-lg">
                <Globe className="h-5 w-5" />
              </div>
              <div>
                <p className="font-medium">認証アプリ</p>
                <p className="text-sm text-muted-foreground">
                  Google Authenticatorなどのアプリで認証
                </p>
              </div>
            </div>
            <Badge variant="outline">無効</Badge>
          </div>

          <Button onClick={handleTwoFactorToggle} variant="outline">
            二要素認証を設定
          </Button>
        </CardContent>
      </Card>

      {/* ログイン履歴 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            ログイン履歴
          </CardTitle>
          <CardDescription>
            最近のログイン活動を確認できます
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* モックデータ - 実際の実装ではAPIから取得 */}
          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium">現在のセッション</p>
                <p className="text-sm text-muted-foreground">
                  Chrome on macOS • 東京, 日本
                </p>
                <p className="text-xs text-muted-foreground">
                  2024年1月15日 14:30
                </p>
              </div>
            </div>
            <Badge className="bg-green-600">現在</Badge>
          </div>

          <div className="flex items-center justify-between p-3 border rounded-lg">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium">モバイルアプリ</p>
                <p className="text-sm text-muted-foreground">
                  iOS Safari • 東京, 日本
                </p>
                <p className="text-xs text-muted-foreground">
                  2024年1月14日 09:15
                </p>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={handleSessionRevoke}>
              セッションを無効化
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* セキュリティのヒント */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Shield className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900">セキュリティのヒント</h4>
              <ul className="text-sm text-blue-800 mt-2 space-y-1">
                <li>• 強力で一意のパスワードを使用してください</li>
                <li>• 二要素認証を有効にしてください</li>
                <li>• 定期的にログイン履歴を確認してください</li>
                <li>• 不審な活動を発見した場合はすぐに報告してください</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
