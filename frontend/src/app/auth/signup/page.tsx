"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { signIn } from "next-auth/react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

function SignUpContent() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleGoogleSignUp = async () => {
    setIsLoading(true);
    try {
      // URLパラメータからcallbackUrlを取得（デフォルトは/dashboard）
      const callbackUrl = searchParams.get("callbackUrl") || "/dashboard";
      await signIn("google", { callbackUrl });
    } catch (error) {
      console.error("Google sign up error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailSignUp = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      alert("パスワードが一致しません");
      return;
    }

    setIsLoading(true);
    try {
      // 実際のサインアップ処理は後で実装
      const response = await fetch("/api/auth/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        // アカウント作成成功後、callbackUrlを引き継いでサインインページへ
        const callbackUrl = searchParams.get("callbackUrl");
        const signinUrl = callbackUrl
          ? `/auth/signin?message=Account created successfully&callbackUrl=${encodeURIComponent(
              callbackUrl,
            )}`
          : "/auth/signin?message=Account created successfully";
        router.push(signinUrl);
      } else {
        const error = await response.json();
        console.error("Sign up failed:", error.message);
      }
    } catch (error) {
      console.error("Email sign up error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-foreground">アカウントを作成</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            すでにアカウントをお持ちの場合は{" "}
            <Link
              href={
                searchParams.get("callbackUrl")
                  ? `/auth/signin?callbackUrl=${searchParams.get("callbackUrl")}`
                  : "/auth/signin"
              }
              className="font-medium text-primary hover:text-primary/80"
            >
              ログイン
            </Link>
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>新規登録</CardTitle>
            <CardDescription>TypeScriptエコシステムの最新情報にアクセスしましょう</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Button
              onClick={handleGoogleSignUp}
              disabled={isLoading}
              variant="outline"
              className="w-full"
            >
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                <path
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  fill="#4285F4"
                />
                <path
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  fill="#34A853"
                />
                <path
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  fill="#FBBC05"
                />
                <path
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  fill="#EA4335"
                />
              </svg>
              Google で登録
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">または</span>
              </div>
            </div>

            <form onSubmit={handleEmailSignUp} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">メールアドレス</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">パスワード</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">パスワード確認</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "登録中..." : "アカウントを作成"}
              </Button>
            </form>

            <div className="text-xs text-muted-foreground text-center">
              アカウントを作成することで、{" "}
              <Link href="/terms" className="text-primary hover:text-primary/80">
                利用規約
              </Link>{" "}
              と{" "}
              <Link href="/privacy" className="text-primary hover:text-primary/80">
                プライバシーポリシー
              </Link>{" "}
              に同意したことになります。
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function SignUpPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full">
            <Card>
              <CardHeader>
                <CardTitle>アカウントを作成</CardTitle>
                <CardDescription>読み込み中...</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      }
    >
      <SignUpContent />
    </Suspense>
  );
}
