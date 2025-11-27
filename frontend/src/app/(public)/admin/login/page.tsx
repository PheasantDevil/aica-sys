import { AdminLoginForm } from "@/components/admin/admin-login-form";
import { AdminSignInPrompt } from "@/components/admin/admin-signin-prompt";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { authOptions } from "@/lib/auth";
import { getServerSession } from "next-auth";

export default async function AdminLoginPage() {
  const session = await getServerSession(authOptions);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4 py-12">
      <Card className="w-full max-w-lg shadow-2xl border-slate-800 bg-slate-900 text-white">
        <CardHeader>
          <CardTitle className="text-2xl">アフィリエイト管理コンソール</CardTitle>
          <CardDescription className="text-slate-300">
            管理者アカウントでサインインし、アクセスキーを入力してください。
          </CardDescription>
        </CardHeader>
        <CardContent>
          {session?.user ? (
            <AdminLoginForm userEmail={session.user.email ?? "admin"} />
          ) : (
            <AdminSignInPrompt />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
