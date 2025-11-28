import { AdminContentPerformance } from "@/components/admin/admin-content-performance";

export default function AdminContentPerformancePage() {
  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-slate-400">CONTENT ANALYTICS</p>
        <h1 className="text-2xl font-semibold text-white mt-1">記事パフォーマンス分析</h1>
        <p className="text-sm text-slate-400 mt-2">
          記事ごとの詳細なパフォーマンス指標を確認し、コンテンツ最適化に活用します。
        </p>
      </div>

      <AdminContentPerformance />
    </div>
  );
}
