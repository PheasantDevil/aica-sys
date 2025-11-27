"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

interface AdminLoginFormProps {
  userEmail: string;
}

export function AdminLoginForm({ userEmail }: AdminLoginFormProps) {
  const [passcode, setPasscode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!passcode) {
      toast.error("アクセスキーを入力してください");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ passcode }),
      });

      const data = await response.json();
      if (!response.ok) {
        toast.error(data.error || "ログインに失敗しました");
        return;
      }

      toast.success("管理者アクセスが付与されました");
      router.push("/admin/affiliates");
      router.refresh();
    } catch (error) {
      console.error("Admin login error", error);
      toast.error("ログイン処理に失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <Label>サインイン中のアカウント</Label>
        <div className="px-3 py-2 rounded border border-slate-800 bg-slate-900 text-slate-200 text-sm">
          {userEmail}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="admin-passcode">管理者アクセスキー</Label>
        <Input
          id="admin-passcode"
          type="password"
          placeholder="アクセスキーを入力"
          value={passcode}
          onChange={(event) => setPasscode(event.target.value)}
          className="bg-slate-900 border-slate-800 text-white placeholder:text-slate-500"
        />
        <p className="text-xs text-slate-400">
          このキーは組織の管理者から共有された情報です。外部に共有しないでください。
        </p>
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "検証中..." : "管理コンソールに入る"}
      </Button>
    </form>
  );
}
