# Phase 11-1: Vercel Speed Insights 導入

## 概要

Vercel Speed Insightsを導入し、Core Web Vitalsに基づいたパフォーマンス測定を強化する。

## 参考資料

- [Vercel Speed Insights Documentation](https://vercel.com/docs/speed-insights)

## 目的

- リアルタイムパフォーマンス測定
- 地理的分布分析
- SEO最適化（Google Page Experience）
- 既存Web Vitals実装との統合

## Speed Insights とは

Vercel公式のパフォーマンス測定ツールで、以下の機能を提供：

- Core Web Vitals の自動測定
- Vercelダッシュボードでの可視化
- デバイス別・環境別・地域別分析
- ルート別パフォーマンス分析

## 実装内容

### 1. パッケージインストール

```bash
cd frontend
npm install @vercel/speed-insights
```

### 2. Next.js アプリケーションに統合

```typescript
// frontend/src/app/layout.tsx
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
      </body>
    </html>
  );
}
```

### 3. 測定されるメトリクス

- **RES** (Real Experience Score): 総合スコア
- **FCP** (First Contentful Paint): 初回コンテンツ表示
- **LCP** (Largest Contentful Paint): 最大コンテンツ表示
- **CLS** (Cumulative Layout Shift): レイアウトシフト
- **INP** (Interaction to Next Paint): インタラクション応答

## 既存実装との関係

### 既存: カスタムWeb Vitals（Phase 7-4）

**ファイル**:

- `frontend/src/lib/web-vitals.ts`
- `frontend/src/components/web-vitals-reporter.tsx`

**機能**:

- 詳細なログ記録
- バックエンドへの送信
- 長期データ保存
- カスタム分析

### 新規: Speed Insights

**機能**:

- Vercelダッシュボード統合
- 地理的分布マップ
- パーセンタイル分析（P75/P90/P95/P99）
- リアルタイム監視

### 役割分担

| 機能         | 既存Web Vitals      | Speed Insights          |
| ------------ | ------------------- | ----------------------- |
| **測定**     | ✅ カスタム実装     | ✅ Vercel統合           |
| **保存**     | ✅ 自社DB（無制限） | ⚠️ 7-90日（プラン依存） |
| **可視化**   | ⚠️ カスタム実装必要 | ✅ Vercel Dashboard     |
| **地理分析** | ❌ なし             | ✅ あり                 |
| **SEO連携**  | ⚠️ 手動             | ✅ 自動                 |
| **コスト**   | 無料                | 無料                    |

**結論**: 両方を併用して相互補完

## コスト

- **追加コスト**: $0（全プランで無料）
- **データ保存**:
  - Hobby: 7日間
  - Pro: 30日間
  - Enterprise: 最大90日間
- **npm パッケージサイズ**: 約5KB（軽量）

## データ保存期間対策

Speed Insightsのデータ保存期間が短いため、既存のカスタムWeb Vitals実装で長期保存を継続：

```
Speed Insights (Vercel Dashboard)
├─ リアルタイム分析: 7-30日
└─ 地理的分布、SEO連携

既存Web Vitals (自社DB)
├─ 長期保存: 無制限
└─ 詳細ログ、カスタム分析
```

## プライバシー対応

Speed Insightsはユーザーデータを収集するため、プライバシーポリシーを更新：

**追加する内容**:

- Vercel Speed Insightsによるパフォーマンスデータ収集
- 匿名化されたメトリクスの送信
- オプトアウト方法

## 実装後の確認

### Vercel Dashboard

1. プロジェクトを選択
2. "Speed Insights" タブをクリック
3. メトリクスが表示されることを確認

### フロントエンド

1. ページアクセス
2. ネットワークタブで `/_vercel/speed-insights` を確認
3. データ送信を確認

## 期待される効果

- ✅ **パフォーマンス可視化**: リアルタイムダッシュボード
- ✅ **SEO向上**: Core Web Vitals改善
- ✅ **ユーザー体験向上**: データドリブンな最適化
- ✅ **地理的分析**: 地域別のパフォーマンス把握
- ✅ **コスト**: 追加コストなし

## 参考リンク

- [Vercel Speed Insights Documentation](https://vercel.com/docs/speed-insights)
- [Core Web Vitals](https://web.dev/vitals/)
- [Google Page Experience](https://developers.google.com/search/docs/appearance/page-experience)
