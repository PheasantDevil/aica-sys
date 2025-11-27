import { AdminReferralLinksTable } from "@/components/admin/admin-referral-links-table";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Suspense } from "react";

export default function AdminReferralLinksPage() {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">REFERRAL LINKS</p>
        <h1 className="text-2xl font-semibold text-white mt-1">リンク管理</h1>
        <p className="text-sm text-slate-400 mt-2">
          すべての紹介リンクを監視し、キャンペーンの有効期限やステータスを更新できます。
        </p>
      </div>

      <Suspense fallback={<LoadingSpinner />}>
        <AdminReferralLinksTable />
      </Suspense>
    </div>
  );
}
