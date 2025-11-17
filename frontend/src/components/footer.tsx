import Link from "next/link";

export function Footer() {
  return (
    <footer className="border-t bg-muted/50">
      <div className="container py-12">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded bg-primary"></div>
              <span className="text-xl font-bold">AICA-SyS</span>
            </div>
            <p className="mt-4 text-sm text-muted-foreground">
              TypeScriptエコシステム特化型のAI自動コンテンツ生成・販売システム
            </p>
          </div>

          <div>
            <h3 className="font-semibold">プロダクト</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li>
                <Link href="/articles" className="text-muted-foreground hover:text-foreground">
                  記事
                </Link>
              </li>
              <li>
                <Link href="/newsletters" className="text-muted-foreground hover:text-foreground">
                  ニュースレター
                </Link>
              </li>
              <li>
                <Link href="/trends" className="text-muted-foreground hover:text-foreground">
                  トレンド
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-muted-foreground hover:text-foreground">
                  料金
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold">サポート</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li>
                <Link href="/help" className="text-muted-foreground hover:text-foreground">
                  ヘルプセンター
                </Link>
              </li>
              <li>
                <Link href="/docs" className="text-muted-foreground hover:text-foreground">
                  ドキュメント
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-muted-foreground hover:text-foreground">
                  お問い合わせ
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold">会社</h3>
            <ul className="mt-4 space-y-2 text-sm">
              <li>
                <Link href="/about" className="text-muted-foreground hover:text-foreground">
                  会社概要
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-foreground">
                  プライバシーポリシー
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-muted-foreground hover:text-foreground">
                  利用規約
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2024 AICA-SyS. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
