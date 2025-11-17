"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { User, CreditCard, Bell, Shield, Settings as SettingsIcon } from "lucide-react";
import { cn } from "@/lib/utils";

type SettingsTab = "profile" | "account" | "notifications" | "security";

interface SettingsNavigationProps {
  activeTab: SettingsTab;
  onTabChange: (tab: SettingsTab) => void;
}

const navigationItems = [
  {
    id: "profile" as const,
    label: "プロフィール",
    description: "個人情報とアバター",
    icon: User,
  },
  {
    id: "account" as const,
    label: "アカウント",
    description: "サブスクリプションと請求",
    icon: CreditCard,
  },
  {
    id: "notifications" as const,
    label: "通知設定",
    description: "メールとプッシュ通知",
    icon: Bell,
  },
  {
    id: "security" as const,
    label: "セキュリティ",
    description: "パスワードとセキュリティ",
    icon: Shield,
  },
];

export function SettingsNavigation({ activeTab, onTabChange }: SettingsNavigationProps) {
  return (
    <Card>
      <CardContent className="p-0">
        <nav className="space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <Button
                key={item.id}
                variant={isActive ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start h-auto p-4",
                  isActive && "bg-primary/10 text-primary",
                )}
                onClick={() => onTabChange(item.id)}
              >
                <div className="flex items-start gap-3">
                  <Icon
                    className={cn(
                      "h-5 w-5 mt-0.5",
                      isActive ? "text-primary" : "text-muted-foreground",
                    )}
                  />
                  <div className="text-left">
                    <div className="font-medium">{item.label}</div>
                    <div className="text-xs text-muted-foreground">{item.description}</div>
                  </div>
                </div>
              </Button>
            );
          })}
        </nav>
      </CardContent>
    </Card>
  );
}
