# ワークフロー自動修正機能ガイド

## 概要

スケジュール実行型ワークフローでエラーが発生した際に、自動的にエラーを検出・修正し、PR を作成してマージまで行う機能です。

## アーキテクチャ概要

```
┌─────────────────────────────────────┐
│ スケジュール実行ワークフロー（失敗） │
│ - Daily Trend Analysis              │
│ - Daily Article Generation          │
│ - Weekly Newsletter Generation      │
│ - Scheduled Backup                  │
│ - Social Media Auto Post            │
└──────────────┬──────────────────────┘
               │ workflow_run イベント
               ▼
┌─────────────────────────────────────┐
│ 自動修正ワークフロー                 │
│ (workflow-auto-fix.yml)             │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
   ┌───▼───┐     ┌────▼────┐
   │ 分析  │     │ 修正    │
   └───┬───┘     └────┬────┘
       │              │
       └──────┬───────┘
              │
       ┌──────▼──────┐
       │ 検証       │
       └──────┬─────┘
              │
    ┌─────────┴─────────┐
    │                   │
成功 ▼              失敗 ▼
    │                   │
PR作成            Issue作成
    │                   │
マージ            手動対応
```

## 処理フロー

### 1. エラー検出

- `workflow_run` イベントでスケジュール実行型ワークフローの失敗を監視
- 失敗したワークフローのログを取得
- エラータイプを自動判定

### 2. エラータイプ判定

以下のエラータイプを自動判定します：

- **format**: フォーマットエラー（black, isort, prettier）
- **migration**: マイグレーションエラー（alembic）
- **dependency**: 依存関係エラー（pip, npm）
- **lint**: リンターエラー（自動修正可能なもの）

### 3. 自動修正

エラータイプに応じて自動修正を実行：

- **format**: `black`, `isort`, `prettier` を実行
- **migration**: 既存の `auto_fix_migrations.py` を実行
- **dependency**: `requirements.txt` / `package.json` を更新
- **lint**: 自動修正可能なリンターエラーを修正

### 4. 変更ファイル検出

- `git diff` で変更ファイルを検出
- frontend/backend/その他の判定
- 該当する検証フローを実行

### 5. 検証

修正後に以下の検証を実行：

- **Frontend**: lint, format, type-check
- **Backend**: lint, format, type-check, migration
- **その他**: 汎用検証

### 6. PR 作成とマージ

- 修正ブランチ `workflow-hotfix-{timestamp}` を作成
- PR を作成（`workflow-hotfix-{timestamp}` → `main`）
- 検証が成功した場合、自動的にマージ
- 検証が失敗した場合、Issue を作成して手動対応を依頼

## 対象ワークフロー

以下のスケジュール実行型ワークフローを監視します：

1. **Daily Trend Analysis** - 毎日午前 10 時（JST）
2. **Daily Article Generation** - 平日午前 9 時（JST）
3. **Weekly Newsletter Generation** - 毎週月曜日午前 8 時（JST）
4. **Scheduled Backup** - 毎日午前 3 時（JST）
5. **Social Media Auto Post** - 毎日 12:00（JST）

## 修正可能なエラー

### 自動修正可能

- ✅ フォーマットエラー（black, isort, prettier）
- ✅ マイグレーションエラー（重複リビジョン ID、複数の head）
- ✅ 依存関係エラー（requirements.txt, package.json）
- ✅ 一部のリンターエラー（自動修正可能なもの）

### 手動対応が必要

- ❌ 型チェックエラー
- ❌ テスト失敗
- ❌ ビルドエラー
- ❌ 実行時エラー

## 通知

### 修正成功時

- PR コメントに成功メッセージを追加
- PR が自動的にマージされる

### 修正失敗時

- Issue を作成（手動対応依頼）
- PR コメントに失敗メッセージを追加

### 自動修正不可時

- Issue を作成（手動対応依頼）
- エラーの詳細情報を含む

## 設定

### Concurrency 制御

各スケジュール実行型ワークフローに `concurrency` を設定しています：

```yaml
concurrency:
  group: { workflow-name }
  cancel-in-progress: false
```

これにより、自動修正ワークフロー実行中は他のワークフローが停止されます。

### 権限

自動修正ワークフローには以下の権限が必要です：

- `contents: write` - コードの修正とコミット
- `pull-requests: write` - PR の作成とマージ
- `issues: write` - Issue の作成

## トラブルシューティング

### 自動修正が実行されない

1. ワークフローがスケジュール実行で失敗しているか確認
2. `workflow_run` イベントが正しく設定されているか確認
3. エラータイプが自動修正可能か確認

### 修正が失敗する

1. PR を確認して修正内容をレビュー
2. 必要に応じて手動で修正を追加
3. 修正後にワークフローを再実行して確認

### 無限ループの防止

- 修正回数は 1 回のみ
- 同じエラーが繰り返される場合は手動対応に切り替え

## 今後の拡張予定

- LINE 通知機能の追加
- より多くのエラータイプへの対応
- 修正履歴の記録と分析
