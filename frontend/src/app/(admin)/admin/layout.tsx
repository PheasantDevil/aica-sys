import { AdminSidebar } from "@/components/admin/admin-sidebar";
import { authOptions } from "@/lib/auth";
import { getServerSession } from "next-auth";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { ReactNode } from "react";

export default async function AdminLayout({ children }: { children: ReactNode }) {
  const session = await getServerSession(authOptions);
  const adminAccess = cookies().get("admin_access");

  if (!session?.user) {
    redirect("/admin/login");
  }

  if (!adminAccess || adminAccess.value !== "granted") {
    redirect("/admin/login");
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <AdminSidebar user={session.user} />
        <main className="flex-1 bg-slate-900/60 border-l border-slate-800 p-6 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
