"use client";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

interface AffiliateRegisterFormProps {
  user: {
    id?: string;
    email?: string | null;
    name?: string | null;
  };
}

export function AffiliateRegisterForm({ user }: AffiliateRegisterFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!agreedToTerms) {
      toast.error("利用規約とプライバシーポリシーに同意してください");
      return;
    }

    if (!user.id) {
      toast.error("ユーザー情報が取得できませんでした。再度ログインしてください。");
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiClient.registerAffiliate(user.id);

      if (response.error) {
        toast.error(response.error || "登録に失敗しました");
        return;
      }

      if (response.data?.success) {
        toast.success("アフィリエイトプログラムへの登録が完了しました！");
        router.push("/affiliate/dashboard");
      } else {
        toast.error("登録に失敗しました");
      }
    } catch (error) {
      console.error("Affiliate registration error:", error);
      toast.error("登録中にエラーが発生しました");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleRegister} className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label htmlFor="email">メールアドレス</Label>
          <input
            id="email"
            type="email"
            value={user.email || ""}
            disabled
            className="mt-1 block w-full rounded-md border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-500"
          />
          <p className="mt-1 text-xs text-gray-500">登録済みのメールアドレスが使用されます</p>
        </div>

        <div className="flex items-start space-x-3">
          <Checkbox
            id="terms"
            checked={agreedToTerms}
            onCheckedChange={(checked) => setAgreedToTerms(checked === true)}
          />
          <Label htmlFor="terms" className="text-sm leading-relaxed">
            <a href="/terms" target="_blank" className="text-blue-600 hover:underline">
              利用規約
            </a>
            および
            <a href="/privacy" target="_blank" className="text-blue-600 hover:underline">
              プライバシーポリシー
            </a>
            に同意します
          </Label>
        </div>
      </div>

      <div className="flex space-x-4">
        <Button type="submit" disabled={isLoading || !agreedToTerms} className="flex-1">
          {isLoading ? "登録中..." : "アフィリエイトプログラムに登録"}
        </Button>
        <Button type="button" variant="outline" onClick={() => router.back()} disabled={isLoading}>
          キャンセル
        </Button>
      </div>
    </form>
  );
}
