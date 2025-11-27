import { AdminAffiliatesTable } from "@/components/admin/admin-affiliates-table";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { Suspense } from "react";

export default function AdminAffiliatesPage() {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">AFFILIATE MANAGEMENT</p>
        <h1 className="text-2xl font-semibold text-white mt-1">パートナー管理</h1>
        <p className="text-sm text-slate-400 mt-2">
          パートナーの承認、ティア設定、パフォーマンス指標を確認できます。
        </p>
      </div>

      <Suspense fallback={<LoadingSpinner />}>
        <AdminAffiliatesTable />
      </Suspense>
    </div>
  );
}
