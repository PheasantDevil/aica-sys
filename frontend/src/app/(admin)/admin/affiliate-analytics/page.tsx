import { AdminAffiliateAnalytics } from "@/components/admin/admin-affiliate-analytics";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Suspense } from "react";

export default function AdminAnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">PERFORMANCE ANALYTICS</p>
        <h1 className="text-2xl font-semibold text-white mt-1">クリック統計</h1>
        <p className="text-sm text-slate-400 mt-2">
          クリック総数やユニークセッションなどの指標を確認し、異常値を早期に検知します。
        </p>
      </div>

      <Suspense fallback={<LoadingSpinner />}>
        <AdminAffiliateAnalytics />
      </Suspense>
    </div>
  );
}
