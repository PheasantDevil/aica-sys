# Phase 10-2: トレンド分析ワークフロー

## 概要

毎日、技術トレンドを分析し、キーワード頻度、トピック分類、上昇トレンドを検出するシステム。

## ファイル構成と役割

```plaintext
Phase 10-2 関連ファイル:
├── .github/workflows/daily-trends.yml           # GitHub Actions ワークフロー定義
├── backend/services/trend_analysis_service.py   # トレンド分析サービス
├── scripts/analyze_trends.py                    # 実行スクリプト
└── docs/phase10-2-trend-analysis.md             # この計画書

データモデル（Phase 10-1から再利用）:
└── backend/models/automated_content.py
    └── TrendDataDB: トレンドデータ保存
```

## トレンド分析機能

### 1. キーワード頻度分析
- 全ソースからキーワード抽出
- 出現頻度カウント
- 時系列での変化追跡

### 2. トピック分類
- 技術カテゴリ分類（AI, Web, Mobile, DevOps等）
- 自動タグ付け
- 関連トピック抽出

### 3. 上昇トレンド検出
- 前日比での上昇率計算
- 新規トレンドの検出
- トレンド強度スコアリング

### 4. データ可視化準備
- JSON形式でデータ保存
- フロントエンドでグラフ表示用
- 月次アーカイブ

## 実行スケジュール

- **頻度**: 毎日
- **時刻**: 午前10時（JST = UTC 1:00）
- **処理時間**: 約5分

## データ保存戦略

### リアルタイムデータ
- 過去7日分: フル詳細
- JSON形式で保存

### アーカイブデータ
- 7日以上: 日次サマリーのみ
- 月次集計に集約
- 容量削減（約90%）

## 出力フォーマット

```json
{
  "date": "2024-10-11",
  "top_trends": [
    {
      "keyword": "Next.js 15",
      "score": 89.5,
      "change": "+15.2%",
      "category": "Web",
      "sources": ["hacker_news", "dev_to", "github"]
    }
  ],
  "rising_trends": [
    {
      "keyword": "Bun 1.0",
      "score": 45.3,
      "growth_rate": "+250%",
      "is_new": true
    }
  ],
  "categories": {
    "AI": 35,
    "Web": 28,
    "DevOps": 18
  }
}
```

## コスト

- **API コスト**: $0（公開APIのみ使用）
- **処理時間**: 約5分
- **データ量**: 約100KB/日 → 3MB/月
- **年間データ**: 約36MB（アーカイブ後は約4MB）

## 期待される効果

- リアルタイムトレンド把握
- データドリブンなコンテンツ戦略
- 検索AIへの価値提供（トレンドデータ）

