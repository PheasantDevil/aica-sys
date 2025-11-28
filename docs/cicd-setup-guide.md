# CI/CD セットアップガイド

Phase 8-1: CI/CDパイプライン構築

## 概要

このガイドでは、AICA-SyS プロジェクトのCI/CDパイプラインのセットアップ方法を説明します。

## GitHub Secrets の設定

### 必須のシークレット

以下のシークレットをGitHubリポジトリに設定してください：

```bash
# リポジトリ > Settings > Secrets and variables > Actions > New repository secret
```

#### Vercel関連

- `VERCEL_TOKEN` - Vercel デプロイメントトークン
- `VERCEL_ORG_ID` - Vercel 組織ID
- `VERCEL_PROJECT_ID` - Vercel プロジェクトID

#### データベース

- `DATABASE_URL` - 本番データベースURL（例: `postgresql://user:pass@host:5432/db`）

#### Redis

- `REDIS_URL` - Redis接続URL（例: `redis://host:6379`）

#### API Keys

- `OPENAI_API_KEY` - OpenAI APIキー
- `GOOGLE_AI_STUDIO_API_KEY` - Google AI Studio APIキー
- `STRIPE_SECRET_KEY` - Stripe シークレットキー

#### Supabase

- `SUPABASE_URL` - Supabase プロジェクトURL
- `SUPABASE_ANON_KEY` - Supabase 匿名キー
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase サービスロールキー

#### その他

- `NEXTAUTH_SECRET` - NextAuth シークレット
- `NEXTAUTH_URL` - NextAuth URL
- `SNYK_TOKEN` - Snyk セキュリティスキャントークン（オプション）

### シークレットの取得方法

#### Vercelトークンの取得

```bash
# Vercel CLIを使用
npx vercel login
npx vercel whoami
npx vercel project ls

# または
# https://vercel.com/account/tokens からトークンを作成
```

#### Supabaseキーの取得

```bash
# Supabase Dashboard
# Project Settings > API > Project API keys
```

## ワークフローの説明

### 1. Backend CI/CD (`backend-ci-cd.yml`)

**トリガー**:

- `main` または `develop` ブランチへのプッシュ
- `backend/` ディレクトリの変更を含むPR

**ジョブ**:

1. **lint-and-format**: コード品質チェック（Black, isort, Flake8）
2. **type-check**: 型チェック（mypy）
3. **test**: ユニットテスト実行とカバレッジ測定
4. **security-scan**: セキュリティスキャン（Safety, Bandit）
5. **build**: アプリケーションビルド検証
6. **deploy-staging**: ステージング環境へのデプロイ（develop）
7. **deploy-production**: 本番環境へのデプロイ（main）

### 2. Frontend CI/CD (`frontend-ci-cd.yml`)

**トリガー**:

- `main` または `develop` ブランチへのプッシュ
- `frontend/` ディレクトリの変更を含むPR

**ジョブ**:

1. **lint-and-format**: ESLintとPrettierチェック
2. **type-check**: TypeScript型チェック
3. **test**: テスト実行とカバレッジ測定
4. **build**: Next.jsビルド
5. **security-scan**: npm auditとSnykスキャン
6. **lighthouse**: パフォーマンス監査
7. **deploy-vercel-preview**: プレビューデプロイ（PR）
8. **deploy-vercel-production**: 本番デプロイ（main）

### 3. Integration Tests (`integration-tests.yml`)

**トリガー**:

- `main` または `develop` ブランチへのプッシュ
- PR作成
- スケジュール実行（毎日午前3時JST）

**ジョブ**:

1. **integration-test**: バックエンドとフロントエンドの統合テスト
2. **e2e-test**: Playwrightによるエンドツーエンドテスト

### 4. PR Checks (`pr-checks.yml`)

**トリガー**:

- プルリクエスト作成・更新

**ジョブ**:

1. **pr-validation**: PRタイトルの検証（Conventional Commits）
2. **changed-files**: 変更ファイルの検出
3. **size-check**: バンドルサイズチェック
4. **dependency-review**: 依存関係レビュー
5. **auto-merge**: Dependabotの自動マージ

## ブランチ戦略

### ブランチ構成

```
main        → 本番環境（Production）
develop     → ステージング環境（Staging）
feature/*   → 機能開発ブランチ
fix/*       → バグ修正ブランチ
hotfix/*    → 緊急修正ブランチ
```

### ブランチ保護ルール

#### mainブランチ

- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass
  - Backend CI/CD
  - Frontend CI/CD
  - Integration Tests
- ✅ Require branches to be up to date
- ✅ Include administrators

#### developブランチ

- ✅ Require pull request before merging
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

## デプロイメントフロー

### 通常デプロイ（機能追加）

```bash
# 1. 機能ブランチを作成
git checkout -b feature/new-feature

# 2. 開発・コミット
git add .
git commit -m "feat: 新機能の追加"

# 3. プッシュ
git push origin feature/new-feature

# 4. PRを作成
gh pr create --base develop --title "feat: 新機能の追加"

# 5. CIが自動実行される
#    - Lint check
#    - Type check
#    - Tests
#    - Security scan

# 6. レビュー・承認後、マージ
gh pr merge --merge

# 7. develop→mainへのPR作成（リリース時）
git checkout develop
git pull
gh pr create --base main --title "release: v1.x.x"

# 8. 承認後、mainにマージ
#    → 本番環境への自動デプロイ
```

### ホットフィックス（緊急修正）

```bash
# 1. mainから直接ブランチを作成
git checkout main
git pull
git checkout -b hotfix/critical-fix

# 2. 修正・コミット
git add .
git commit -m "fix: 緊急修正"

# 3. プッシュとPR
git push origin hotfix/critical-fix
gh pr create --base main --title "fix: 緊急修正"

# 4. CIパス後、即座にマージ
gh pr merge --merge

# 5. developにもマージ
git checkout develop
git merge main
git push
```

## ローカルでのCI検証

### バックエンド

```bash
cd backend

# フォーマットチェック
black --check .
isort --check .

# リンティング
flake8 .

# 型チェック
mypy . --ignore-missing-imports

# テスト
pytest --cov=.

# セキュリティスキャン
safety check
bandit -r .
```

### フロントエンド

```bash
cd frontend

# リンティング
npm run lint

# 型チェック
npx tsc --noEmit

# フォーマットチェック
npx prettier --check "src/**/*.{ts,tsx,js,jsx}"

# テスト
npm run test

# ビルド
npm run build

# セキュリティ
npm audit
```

## トラブルシューティング

### ワークフローが失敗する

**症状**: CI/CDワークフローが赤くなる

**確認事項**:

1. ログを確認（Actions タブ）
2. ローカルで同じコマンドを実行
3. 依存関係の問題をチェック

### デプロイが失敗する

**症状**: デプロイジョブが失敗する

**確認事項**:

1. GitHub Secretsが正しく設定されているか
2. デプロイ先のサービスが稼働しているか
3. ネットワーク接続の問題がないか

### テストがタイムアウトする

**症状**: テストジョブが30分でタイムアウト

**対策**:

1. テストを並列化
2. 不要なテストをスキップ
3. タイムアウト時間を延長

## ベストプラクティス

### コミットメッセージ

Conventional Commits形式を使用：

```
feat: 新機能追加
fix: バグ修正
docs: ドキュメント更新
style: コードフォーマット
refactor: リファクタリング
perf: パフォーマンス改善
test: テスト追加・修正
chore: その他の変更
ci: CI/CD関連の変更
```

### PRレビュー

チェックリスト：

- [ ] コードレビュー完了
- [ ] 全てのCIチェックが成功
- [ ] テストカバレッジが維持されている
- [ ] ドキュメントが更新されている
- [ ] セキュリティスキャンが合格

### デプロイメント

- **小さく頻繁に**: 大きな変更を避ける
- **テスト重視**: 十分なテストカバレッジ
- **監視**: デプロイ後の監視を徹底
- **ロールバック準備**: 常にロールバック可能な状態を維持

## 参考資料

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vercel Deployment Documentation](https://vercel.com/docs/deployments)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
