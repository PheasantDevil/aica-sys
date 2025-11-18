"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Bell, Mail, Smartphone, Globe } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function NotificationSettings() {
  const [settings, setSettings] = useState({
    email: {
      newsletter: true,
      articles: true,
      trends: false,
      security: true,
      marketing: false,
    },
    push: {
      articles: true,
      trends: false,
      security: true,
    },
    browser: {
      articles: true,
      trends: false,
      security: true,
    },
  });

  const [isLoading, setIsLoading] = useState(false);

  const handleSettingChange = (
    category: keyof typeof settings,
    setting: string,
    value: boolean,
  ) => {
    setSettings((prev) => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value,
      },
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);

    try {
      // 実際の実装ではAPIを呼び出して設定を保存
      await new Promise((resolve) => setTimeout(resolve, 1000));
      toast.success("通知設定が保存されました");
    } catch (error) {
      console.error("Settings save error:", error);
      toast.error("設定の保存に失敗しました");
    } finally {
      setIsLoading(false);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "email":
        return Mail;
      case "push":
        return Smartphone;
      case "browser":
        return Globe;
      default:
        return Bell;
    }
  };

  const getTitle = (type: string) => {
    switch (type) {
      case "email":
        return "メール通知";
      case "push":
        return "プッシュ通知";
      case "browser":
        return "ブラウザ通知";
      default:
        return "通知";
    }
  };

  const getDescription = (type: string) => {
    switch (type) {
      case "email":
        return "メールで通知を受け取ります";
      case "push":
        return "モバイルデバイスでプッシュ通知を受け取ります";
      case "browser":
        return "ブラウザで通知を受け取ります";
      default:
        return "通知設定";
    }
  };

  return (
    <div className="space-y-6">
      {Object.entries(settings).map(([category, categorySettings]) => {
        const Icon = getIcon(category);

        return (
          <Card key={category}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Icon className="h-5 w-5" />
                {getTitle(category)}
              </CardTitle>
              <CardDescription>{getDescription(category)}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(categorySettings).map(([setting, value]) => {
                const settingLabels: Record<string, string> = {
                  newsletter: "ニュースレター",
                  articles: "新しい記事",
                  trends: "トレンド分析",
                  security: "セキュリティ",
                  marketing: "マーケティング",
                };

                const settingDescriptions: Record<string, string> = {
                  newsletter: "週刊ニュースレターの配信通知",
                  articles: "新しい記事が公開されたときの通知",
                  trends: "重要なトレンド分析の通知",
                  security: "ログインやセキュリティ関連の通知",
                  marketing: "プロモーションやお知らせの通知",
                };

                return (
                  <div key={setting} className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label htmlFor={`${category}-${setting}`}>{settingLabels[setting]}</Label>
                      <p className="text-sm text-muted-foreground">
                        {settingDescriptions[setting]}
                      </p>
                    </div>
                    <Switch
                      id={`${category}-${setting}`}
                      checked={value}
                      onCheckedChange={(checked) =>
                        handleSettingChange(category as keyof typeof settings, setting, checked)
                      }
                    />
                  </div>
                );
              })}
            </CardContent>
          </Card>
        );
      })}

      {/* 通知頻度設定 */}
      <Card>
        <CardHeader>
          <CardTitle>通知頻度</CardTitle>
          <CardDescription>通知の頻度を調整できます</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <Label>メール通知頻度</Label>
                <p className="text-sm text-muted-foreground">メール通知の頻度を選択してください</p>
              </div>
              <Button variant="outline" size="sm" disabled>
                即座
              </Button>
            </div>

            <Separator />

            <div className="flex items-center justify-between">
              <div>
                <Label>プッシュ通知頻度</Label>
                <p className="text-sm text-muted-foreground">
                  プッシュ通知の頻度を選択してください
                </p>
              </div>
              <Button variant="outline" size="sm" disabled>
                即座
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 保存ボタン */}
      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? "保存中..." : "設定を保存"}
        </Button>
      </div>
    </div>
  );
}
