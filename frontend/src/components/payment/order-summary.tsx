'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Check, Crown, Star } from 'lucide-react';

interface OrderSummaryProps {
  plan: string;
}

const planDetails = {
  premium: {
    name: 'プレミアムプラン',
    price: 1980,
    period: '月',
    icon: Crown,
    color: 'bg-primary',
    features: [
      '日次トレンドレポート',
      '全記事の閲覧',
      'プレミアムコンテンツ',
      '優先サポート',
      'API アクセス',
      'カスタム分析',
      '無制限ダウンロード',
      '早期アクセス機能',
    ],
  },
  enterprise: {
    name: 'エンタープライズプラン',
    price: 0,
    period: '',
    icon: Star,
    color: 'bg-purple-500',
    features: [
      '無制限アクセス',
      'チーム管理機能',
      'カスタムブランディング',
      '専任サポート',
      'オンプレミス対応',
      'SLA保証',
      'カスタム統合',
      '専用アカウントマネージャー',
    ],
  },
};

export function OrderSummary({ plan }: OrderSummaryProps) {
  const planInfo = planDetails[plan as keyof typeof planDetails] || planDetails.premium;
  const Icon = planInfo.icon;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Icon className="h-5 w-5" />
            注文内容
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${planInfo.color} text-white`}>
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <p className="font-medium">{planInfo.name}</p>
                <p className="text-sm text-muted-foreground">
                  {plan === 'enterprise' ? 'カスタム価格' : '月額プラン'}
                </p>
              </div>
            </div>
            
            {plan !== 'enterprise' && (
              <div className="text-right">
                <p className="text-2xl font-bold">¥{planInfo.price.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">/{planInfo.period}</p>
              </div>
            )}
          </div>
          
          <Separator />
          
          <div className="space-y-2">
            <h4 className="font-medium">含まれる機能</h4>
            <ul className="space-y-2">
              {planInfo.features.map((feature, index) => (
                <li key={index} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-green-600 flex-shrink-0" />
                  <span className="text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>料金詳細</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between">
            <span>サブスクリプション料金</span>
            <span>
              {plan === 'enterprise' ? 'カスタム' : `¥${planInfo.price.toLocaleString()}`}
            </span>
          </div>
          
          <div className="flex justify-between">
            <span>税金</span>
            <span>含む</span>
          </div>
          
          <Separator />
          
          <div className="flex justify-between font-medium">
            <span>合計</span>
            <span>
              {plan === 'enterprise' ? 'お問い合わせください' : `¥${planInfo.price.toLocaleString()}/月`}
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>お支払いについて</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm text-muted-foreground space-y-2">
            <p>• お支払いは毎月自動的に更新されます</p>
            <p>• いつでもキャンセル可能です</p>
            <p>• 14日間の無料トライアルが含まれています</p>
            <p>• 返金保証：30日間</p>
          </div>
          
          <div className="pt-4">
            <Badge variant="outline" className="w-full justify-center">
              <Check className="h-3 w-3 mr-1" />
              安全な決済処理
            </Badge>
          </div>
        </CardContent>
      </Card>

      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Check className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <p className="font-medium text-green-800">
                今すぐアクティベート
              </p>
              <p className="text-sm text-green-700">
                お支払い完了後、すぐにプレミアム機能をご利用いただけます
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
