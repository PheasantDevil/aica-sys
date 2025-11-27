"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { LayoutDashboard, LineChart, Link2, LogOut } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

interface AdminSidebarProps {
  user: {
    name?: string | null;
    email?: string | null;
  };
}

const navItems = [
  {
    href: "/admin/affiliates",
    label: "パートナー管理",
    icon: LayoutDashboard,
  },
  {
    href: "/admin/affiliate-links",
    label: "リンク管理",
    icon: Link2,
  },
  {
    href: "/admin/affiliate-analytics",
    label: "クリック統計",
    icon: LineChart,
  },
];

export function AdminSidebar({ user }: AdminSidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await fetch("/api/admin/logout", { method: "POST" });
      toast.success("管理者アクセスを解除しました");
      router.push("/admin/login");
      router.refresh();
    } catch (error) {
      console.error("Admin logout error", error);
      toast.error("ログアウトに失敗しました");
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <aside className="w-72 bg-slate-950 border-r border-slate-800 flex flex-col">
      <div className="px-6 py-6 border-b border-slate-800">
        <h1 className="text-lg font-semibold text-white">Affiliate Admin</h1>
        <p className="text-xs text-slate-400 mt-2">{user.email}</p>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-slate-800 text-white"
                  : "text-slate-300 hover:text-white hover:bg-slate-900",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <Button
          variant="ghost"
          className="w-full justify-start text-slate-300 hover:text-white hover:bg-slate-900"
          onClick={handleLogout}
          disabled={isLoggingOut}
        >
          <LogOut className="h-4 w-4 mr-2" />
          {isLoggingOut ? "ログアウト中..." : "管理者アクセス解除"}
        </Button>
      </div>
    </aside>
  );
}
