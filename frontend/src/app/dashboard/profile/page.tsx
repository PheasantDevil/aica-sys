"use client";

import { Footer } from "@/components/footer";
import { Header } from "@/components/header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { User, Mail, Calendar, Shield, Save, Upload, Trash2 } from "lucide-react";
import { useSession } from "next-auth/react";
import { useState } from "react";

export default function ProfilePage() {
  const { data: session, update } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: session?.user?.name || "",
    email: session?.user?.email || "",
    bio: "",
    website: "",
    twitter: "",
    github: "",
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // 実際の実装では、APIを呼び出してプロフィールを更新
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // セッションを更新
      await update({
        ...session,
        user: {
          ...session?.user,
          name: formData.name,
        },
      });

      console.log("Profile updated successfully");
    } catch (error) {
      console.error("Error updating profile:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 実際の実装では、ファイルをアップロードしてURLを取得
    console.log("Avatar upload:", file);
  };

  const getSubscriptionBadge = () => {
    // 実際の実装では、ユーザーのサブスクリプション状態を取得
    return <Badge className="bg-green-100 text-green-800">プレミアム</Badge>;
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">プロフィール設定</h1>
          <p className="text-muted-foreground mt-2">アカウント情報とプロフィールを管理できます</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* プロフィール情報 */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <User className="mr-2 h-5 w-5" />
                  基本情報
                </CardTitle>
                <CardDescription>プロフィールの基本情報を設定してください</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* アバター */}
                <div className="flex items-center space-x-6">
                  <div className="relative">
                    <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center">
                      {session?.user?.image ? (
                        <img
                          src={session.user.image}
                          alt="Avatar"
                          className="h-20 w-20 rounded-full object-cover"
                        />
                      ) : (
                        <User className="h-8 w-8 text-muted-foreground" />
                      )}
                    </div>
                    <label className="absolute -bottom-2 -right-2 bg-primary text-primary-foreground rounded-full p-1 cursor-pointer hover:bg-primary/90">
                      <Upload className="h-4 w-4" />
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleAvatarUpload}
                        className="hidden"
                      />
                    </label>
                  </div>
                  <div>
                    <p className="text-sm font-medium">プロフィール画像</p>
                    <p className="text-xs text-muted-foreground">JPG, PNG, GIF (最大2MB)</p>
                  </div>
                </div>

                <Separator />

                {/* フォーム */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">表示名</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => handleInputChange("name", e.target.value)}
                      placeholder="表示名を入力"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">メールアドレス</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      disabled
                      className="bg-muted"
                    />
                    <p className="text-xs text-muted-foreground">メールアドレスは変更できません</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">自己紹介</Label>
                  <textarea
                    id="bio"
                    value={formData.bio}
                    onChange={(e) => handleInputChange("bio", e.target.value)}
                    placeholder="自己紹介を入力してください"
                    className="w-full min-h-[100px] px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="website">ウェブサイト</Label>
                    <Input
                      id="website"
                      value={formData.website}
                      onChange={(e) => handleInputChange("website", e.target.value)}
                      placeholder="https://example.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="twitter">Twitter</Label>
                    <Input
                      id="twitter"
                      value={formData.twitter}
                      onChange={(e) => handleInputChange("twitter", e.target.value)}
                      placeholder="@username"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="github">GitHub</Label>
                  <Input
                    id="github"
                    value={formData.github}
                    onChange={(e) => handleInputChange("github", e.target.value)}
                    placeholder="username"
                  />
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleSave} disabled={isLoading}>
                    <Save className="mr-2 h-4 w-4" />
                    {isLoading ? "保存中..." : "保存"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* サイドバー */}
          <div className="space-y-6">
            {/* アカウント情報 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="mr-2 h-5 w-5" />
                  アカウント情報
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">プラン</span>
                  {getSubscriptionBadge()}
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">メンバー登録日</span>
                  <span className="text-sm text-muted-foreground">
                    {new Date().toLocaleDateString("ja-JP")}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">最終ログイン</span>
                  <span className="text-sm text-muted-foreground">
                    {new Date().toLocaleDateString("ja-JP")}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* 危険な操作 */}
            <Card>
              <CardHeader>
                <CardTitle className="text-destructive">危険な操作</CardTitle>
                <CardDescription>これらの操作は取り消すことができません</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button variant="destructive" className="w-full">
                  <Trash2 className="mr-2 h-4 w-4" />
                  アカウントを削除
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
