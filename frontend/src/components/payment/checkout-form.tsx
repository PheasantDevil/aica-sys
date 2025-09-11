'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { useSubscription } from '@/hooks/use-subscription';
import { getStripe } from '@/lib/stripe';
import { CreditCard, Lock, Shield, Zap } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

interface CheckoutFormProps {
  priceId?: string | null;
  plan: string;
}

export function CheckoutForm({ priceId, plan }: CheckoutFormProps) {
  const { handleUpgrade, isUpgrading } = useSubscription();
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!priceId) {
      toast.error('価格IDが見つかりません');
      return;
    }

    setIsProcessing(true);
    
    try {
      await handleUpgrade(priceId);
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error('決済処理中にエラーが発生しました');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleStripeCheckout = async () => {
    if (!priceId) {
      toast.error('価格IDが見つかりません');
      return;
    }

    setIsProcessing(true);
    
    try {
      const response = await fetch('/api/stripe/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ priceId }),
      });

      if (!response.ok) {
        throw new Error('Failed to create checkout session');
      }

      const { url } = await response.json();
      
      if (url) {
        window.location.href = url;
      }
    } catch (error) {
      console.error('Stripe checkout error:', error);
      toast.error('決済セッションの作成に失敗しました');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            お支払い情報
          </CardTitle>
          <CardDescription>
            安全な決済処理のため、Stripeを使用しています
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="firstName">名</Label>
              <Input id="firstName" placeholder="太郎" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="lastName">姓</Label>
              <Input id="lastName" placeholder="田中" required />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">メールアドレス</Label>
            <Input 
              id="email" 
              type="email" 
              placeholder="tanaka@example.com" 
              required 
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="country">国・地域</Label>
            <Input id="country" placeholder="日本" required />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="postalCode">郵便番号</Label>
            <Input id="postalCode" placeholder="123-4567" required />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>決済方法</CardTitle>
          <CardDescription>
            Stripe Checkoutで安全にお支払いください
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 border rounded-lg bg-muted/50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <CreditCard className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-medium">Stripe Checkout</p>
                <p className="text-sm text-muted-foreground">
                  クレジットカード、デビットカード、その他の決済方法に対応
                </p>
              </div>
            </div>
          </div>
          
          <Button 
            onClick={handleStripeCheckout}
            disabled={isProcessing || isUpgrading}
            className="w-full"
            size="lg"
          >
            {isProcessing || isUpgrading ? (
              <>
                <Zap className="h-4 w-4 mr-2 animate-spin" />
                処理中...
              </>
            ) : (
              <>
                <Lock className="h-4 w-4 mr-2" />
                安全にお支払い
              </>
            )}
          </Button>
          
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Shield className="h-4 w-4" />
            <span>SSL暗号化により保護されています</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>お支払いの安全性</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <Shield className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <p className="font-medium">PCI DSS準拠</p>
              <p className="text-sm text-muted-foreground">
                業界最高レベルのセキュリティ標準に準拠
              </p>
            </div>
          </div>
          
          <Separator />
          
          <div className="flex items-start gap-3">
            <Lock className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="font-medium">SSL暗号化</p>
              <p className="text-sm text-muted-foreground">
                すべての通信が256ビットSSLで暗号化
              </p>
            </div>
          </div>
          
          <Separator />
          
          <div className="flex items-start gap-3">
            <Zap className="h-5 w-5 text-purple-600 mt-0.5" />
            <div>
              <p className="font-medium">即座にアクティベート</p>
              <p className="text-sm text-muted-foreground">
                お支払い完了後、すぐにプレミアム機能をご利用いただけます
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
