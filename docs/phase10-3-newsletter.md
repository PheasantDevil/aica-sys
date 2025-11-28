# Phase 10-3: 週次ニュースレター生成

## 概要

毎週月曜日、週間トレンドをまとめたニュースレターを自動生成するシステム。

## ファイル構成と役割

```plaintext
Phase 10-3 関連ファイル:
├── .github/workflows/weekly-newsletter.yml      # GitHub Actions ワークフロー定義
├── scripts/generate_newsletter.py               # 実行スクリプト
└── docs/phase10-3-newsletter.md                 # この計画書

サービス層（Phase 10-1, 10-2から再利用）:
├── backend/services/content_automation_service.py  # コンテンツ生成
├── backend/services/trend_analysis_service.py      # トレンド分析
└── backend/models/automated_content.py
    └→ AutomatedContentDB: ニュースレター保存
```

## ニュースレター構成

### 1. 週間ハイライト

- トップ5トレンド
- 各トレンドの簡潔な説明
- なぜ重要か

### 2. 今週の記事ピックアップ

- 生成された記事から上位5記事
- 読者の反応が良かった記事

### 3. 次週の注目トピック

- 上昇トレンド予測
- 注目すべき技術

### 4. コミュニティハイライト

- GitHubトレンディング
- 注目のディスカッション

## 実行スケジュール

- **頻度**: 毎週月曜日
- **時刻**: 午前8時（JST = UTC 23:00 日曜）
- **処理時間**: 約10分

## データソース

- 前週のTrendDataDB（7日分）
- 前週のAutomatedContentDB（記事）
- 前週のSourceDataDB（生の情報）

## 出力フォーマット

```markdown
# AICA-SyS 週刊ニュースレター

## {Week of MM/DD/YYYY}

### 📈 今週のトップトレンド

1. **{Trend 1}** - {Score}pt
   {簡潔な説明}

### 📚 今週の人気記事

1. [{Article Title}](/articles/{slug})
   {サマリー}

### 🔮 来週の注目トピック

- {Rising Trend 1}: {予測}
- {Rising Trend 2}: {予測}

### 🌟 コミュニティハイライト

- {GitHub Repo}: {説明}
```

## コスト

- **OpenAI API**: 約$0.01/週（サマリー生成）
- **処理時間**: 約10分
- **GitHub Actions**: 無料枠内
- **月間コスト**: 約$0.05

## 期待される効果

- 購読者エンゲージメント向上
- リテンション率向上（+30%）
- ブランド認知度向上
- コミュニティ形成
