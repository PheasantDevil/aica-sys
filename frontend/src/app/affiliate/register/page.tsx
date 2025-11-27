import { AffiliateRegisterForm } from "@/components/affiliate/affiliate-register-form";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { authOptions } from "@/lib/auth";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

export default async function AffiliateRegisterPage() {
  const session = await getServerSession(authOptions);

  if (!session || !session.user) {
    redirect("/auth/signin?callbackUrl=/affiliate/register");
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">アフィリエイトプログラムに登録</CardTitle>
            <CardDescription>
              AICA-SySのアフィリエイトプログラムに参加して、紹介報酬を獲得しましょう。
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AffiliateRegisterForm user={session.user} />
          </CardContent>
        </Card>

        {/* プログラムの説明 */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">アフィリエイトプログラムについて</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm text-gray-600">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">報酬について</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>紹介したユーザーが有料プランに加入すると、報酬が発生します</li>
                <li>報酬率はティア（ブロンズ、シルバー、ゴールド、プラチナ）によって異なります</li>
                <li>最低支払い額に達すると、自動的に支払いリクエストが作成されます</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">リンクの生成</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>登録後、ダッシュボードから紹介リンクを生成できます</li>
                <li>キャンペーンごとにリンクを管理できます</li>
                <li>リンクの有効期限を設定できます</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">統計とレポート</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>クリック数、コンバージョン数をリアルタイムで確認できます</li>
                <li>詳細な統計レポートをダウンロードできます</li>
                <li>コミッション履歴を確認できます</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
