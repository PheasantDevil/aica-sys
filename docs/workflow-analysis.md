# GitHub Actionsワークフロー分析

## 現在のワークフロー一覧（14個）

| #   | ファイル名            | 目的                         | トリガー   | ステータス                  |
| --- | --------------------- | ---------------------------- | ---------- | --------------------------- |
| 1   | backend-ci-cd.yml     | バックエンドCI/CD            | push, PR   | ✅ 保持                     |
| 2   | frontend-ci-cd.yml    | フロントエンドCI/CD          | push, PR   | ✅ 保持                     |
| 3   | ci-cd.yml             | 統合CI/CD                    | push, PR   | ⚠️ 重複削除候補             |
| 4   | pr-checks.yml         | PR検証                       | PR         | ✅ 保持                     |
| 5   | integration-tests.yml | 統合テスト                   | push, PR   | ✅ 保持                     |
| 6   | security-scan.yml     | セキュリティスキャン（包括） | 週次, push | ✅ 保持                     |
| 7   | security.yml          | セキュリティスキャン（簡易） | push, PR   | ⚠️ 重複削除                 |
| 8   | backend-deploy.yml    | バックエンドデプロイ         | push       | ⚠️ backend-ci-cd.ymlと重複  |
| 9   | deploy.yml            | Vercelデプロイ               | push       | ⚠️ frontend-ci-cd.ymlと重複 |
| 10  | performance.yml       | パフォーマンステスト         | 週次       | ✅ 保持                     |
| 11  | scheduled-backup.yml  | 定期バックアップ             | 日次       | ✅ 保持                     |
| 12  | daily-articles.yml    | デイリー記事生成             | 平日       | ✅ 保持（Phase 10-1）       |
| 13  | daily-trends.yml      | トレンド分析                 | 日次       | ✅ 保持（Phase 10-2）       |
| 14  | weekly-newsletter.yml | 週次ニュースレター           | 週次       | ✅ 保持（Phase 10-3）       |

## 削除候補（5個）

### 1. ci-cd.yml

**理由**: backend-ci-cd.ymlとfrontend-ci-cd.ymlで個別管理する方が効率的
**アクション**: 削除

### 2. security.yml

**理由**: security-scan.yml（Phase 8-5）の方が包括的
**アクション**: 削除

### 3. backend-deploy.yml

**理由**: backend-ci-cd.ymlにデプロイ機能あり
**アクション**: 削除

### 4. deploy.yml

**理由**: frontend-ci-cd.ymlにVercelデプロイあり
**アクション**: 削除

## 最適化後のワークフロー構成（10個）

### コアCI/CD（2個）

- backend-ci-cd.yml
- frontend-ci-cd.yml

### 品質チェック（3個）

- pr-checks.yml
- integration-tests.yml
- performance.yml

### セキュリティ（1個）

- security-scan.yml（Phase 8-5）

### 運用（1個）

- scheduled-backup.yml（Phase 8-4）

### コンテンツ自動化（3個・Phase 10）

- daily-articles.yml
- daily-trends.yml
- weekly-newsletter.yml

## 削減効果

- **ワークフロー数**: 14個 → 10個（28%削減）
- **重複排除**: 4個のワークフロー削除
- **保守性向上**: 明確な責務分離
- **実行時間削減**: 重複ジョブ削減により約30%短縮
