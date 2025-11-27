"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import { useApiCall } from "@/hooks/use-api";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Wallet } from "lucide-react";

interface Payout {
  id: number;
  amount: number;
  status: string;
  payment_method: string | null;
  transaction_id: string | null;
  requested_at: string;
  completed_at: string | null;
}

interface CommissionHistoryProps {
  affiliateId: number;
}

export function CommissionHistory({ affiliateId }: CommissionHistoryProps) {
  const [payouts, setPayouts] = useState<Payout[]>([]);
  const { loading, execute } = useApiCall<{ payouts: Payout[]; count: number }>();

  useEffect(() => {
    loadPayouts();
  }, [affiliateId]);

  const loadPayouts = async () => {
    const result = await execute(() => apiClient.getPayouts(affiliateId, 10));
    if (result) {
      setPayouts(result.payouts || []);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("ja-JP", {
      style: "currency",
      currency: "JPY",
    }).format(amount);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleDateString("ja-JP");
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive"> = {
      pending: "secondary",
      completed: "default",
      failed: "destructive",
    };

    const labels: Record<string, string> = {
      pending: "保留中",
      completed: "完了",
      failed: "失敗",
    };

    return <Badge variant={variants[status] || "default"}>{labels[status] || status}</Badge>;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>支払い履歴</CardTitle>
            <CardDescription>最近の支払いリクエストと履歴</CardDescription>
          </div>
          <Wallet className="h-5 w-5 text-gray-400" />
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-8 text-gray-600">読み込み中...</div>
        ) : payouts.length === 0 ? (
          <div className="text-center py-8 text-gray-600">
            <p className="text-sm">支払い履歴がありません</p>
          </div>
        ) : (
          <div className="space-y-4">
            {payouts.map((payout) => (
              <div
                key={payout.id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="font-semibold">{formatCurrency(payout.amount)}</span>
                    {getStatusBadge(payout.status)}
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>
                      <span className="font-medium">リクエスト日:</span>{" "}
                      {formatDate(payout.requested_at)}
                    </div>
                    {payout.completed_at && (
                      <div>
                        <span className="font-medium">完了日:</span>{" "}
                        {formatDate(payout.completed_at)}
                      </div>
                    )}
                    {payout.payment_method && (
                      <div>
                        <span className="font-medium">支払い方法:</span> {payout.payment_method}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
