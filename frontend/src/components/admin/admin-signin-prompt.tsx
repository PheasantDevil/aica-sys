"use client";

import { Button } from "@/components/ui/button";
import { signIn } from "next-auth/react";

export function AdminSignInPrompt() {
  return (
    <div className="space-y-6 text-slate-200">
      <p className="text-sm leading-relaxed">
        管理者コンソールにアクセスするには、まず認証済みのアカウントでサインインしてください。
        サインイン後、管理者アクセスキーの入力画面に進みます。
      </p>
      <Button className="w-full" onClick={() => signIn("google", { callbackUrl: "/admin/login" })}>
        Google アカウントでサインイン
      </Button>
    </div>
  );
}
