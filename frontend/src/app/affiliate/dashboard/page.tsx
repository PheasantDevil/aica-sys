import { AffiliateDashboardContent } from "@/components/affiliate/affiliate-dashboard-content";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { authOptions } from "@/lib/auth";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import { Suspense } from "react";

export default async function AffiliateDashboardPage() {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    redirect("/auth/signin?callbackUrl=/affiliate/dashboard");
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">アフィリエイトダッシュボード</h1>
          <p className="mt-2 text-sm text-gray-600">
            紹介リンクの管理、統計の確認、コミッション履歴の閲覧ができます
          </p>
        </div>

        <Suspense fallback={<LoadingSpinner />}>
          <AffiliateDashboardContent user={session.user} />
        </Suspense>
      </div>
    </div>
  );
}
