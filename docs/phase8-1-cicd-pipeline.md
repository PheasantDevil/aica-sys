# Phase 8-1: CI/CDパイプライン構築

## 目的

GitHub Actionsを使用した自動テスト・自動デプロイパイプラインを構築し、開発効率とコード品質を向上させる。

## CI/CDパイプライン設計

### 1. CI（継続的インテグレーション）

```
┌─────────────┐
│  Git Push   │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────┐
│  GitHub Actions Workflow                    │
│  ├─ Checkout Code                          │
│  ├─ Setup Environment                      │
│  ├─ Install Dependencies                   │
│  ├─ Run Linters (ESLint, Black, isort)    │
│  ├─ Type Check (TypeScript, mypy)         │
│  ├─ Run Unit Tests                         │
│  ├─ Run Integration Tests                  │
│  ├─ Code Coverage Report                   │
│  ├─ Security Scan (npm audit, safety)     │
│  └─ Build Application                      │
└──────┬──────────────────────────────────────┘
       │
┌──────▼──────┐
│  CD Process │
└─────────────┘
```

### 2. CD（継続的デリバリー）

```
┌─────────────┐
│  CI Success │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────┐
│  Deploy to Staging                          │
│  ├─ Build Docker Images                     │
│  ├─ Push to Container Registry              │
│  ├─ Deploy to Staging Environment           │
│  ├─ Run Smoke Tests                         │
│  └─ Health Check                            │
└──────┬──────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────┐
│  Deploy to Production (Manual Approval)     │
│  ├─ Blue/Green Deployment                   │
│  ├─ Health Check                            │
│  ├─ Smoke Tests                             │
│  ├─ Switch Traffic                          │
│  └─ Monitor Metrics                         │
└─────────────────────────────────────────────┘
```

## GitHub Actions ワークフローファイル

### 1. バックエンドCI/CD

```yaml
# .github/workflows/backend-ci-cd.yml
name: Backend CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run linters
        run: |
          cd backend
          black --check .
          isort --check .
          flake8 .
      
      - name: Type checking
        run: |
          cd backend
          mypy .
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=. --cov-report=xml
      
      - name: Security scan
        run: |
          cd backend
          safety check
          bandit -r .
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
  
  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Staging
        run: |
          # Staging環境へのデプロイ
          echo "Deploying to staging..."
  
  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://api.aica-sys.com
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: |
          docker build -t aica-sys-backend:${{ github.sha }} backend/
      
      - name: Push to registry
        run: |
          # Container registryへのプッシュ
          echo "Pushing to registry..."
      
      - name: Deploy to Production
        run: |
          # 本番環境へのデプロイ
          echo "Deploying to production..."
```

### 2. フロントエンドCI/CD

```yaml
# .github/workflows/frontend-ci-cd.yml
name: Frontend CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run linters
        run: |
          cd frontend
          npm run lint
      
      - name: Type checking
        run: |
          cd frontend
          npm run type-check
      
      - name: Run tests
        run: |
          cd frontend
          npm run test
      
      - name: Build
        run: |
          cd frontend
          npm run build
      
      - name: Security audit
        run: |
          cd frontend
          npm audit --production
  
  deploy-vercel:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### 3. 統合テストワークフロー

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup environment
        run: |
          # 環境変数設定
          cp .env.example .env
      
      - name: Run backend
        run: |
          cd backend
          python -m uvicorn main:app &
          sleep 10
      
      - name: Run frontend
        run: |
          cd frontend
          npm run build
          npm start &
          sleep 10
      
      - name: Run integration tests
        run: |
          node scripts/test-api-optimization.js
          node scripts/test-cache-system.js
          node scripts/comprehensive-load-test.js --users=10 --duration=30
```

## 環境変数管理

### GitHub Secrets設定

```bash
# 必要なシークレット
VERCEL_TOKEN              # Vercel デプロイトークン
VERCEL_ORG_ID             # Vercel 組織ID
VERCEL_PROJECT_ID         # Vercel プロジェクトID
DATABASE_URL              # データベースURL
REDIS_URL                 # Redis URL
OPENAI_API_KEY            # OpenAI APIキー
GOOGLE_AI_STUDIO_API_KEY  # Google AI Studio APIキー
STRIPE_SECRET_KEY         # Stripe シークレットキー
SUPABASE_URL              # Supabase URL
SUPABASE_ANON_KEY         # Supabase 匿名キー
```

## デプロイメント戦略

### 1. プルリクエストベースのデプロイ

```
PR作成 → CI実行 → レビュー → マージ → 自動デプロイ
```

### 2. ブランチ戦略

```
main       → 本番環境 (Production)
develop    → ステージング環境 (Staging)
feature/*  → プレビュー環境 (Preview)
```

### 3. デプロイメントチェックリスト

- [ ] 全てのテストが成功
- [ ] コードカバレッジ80%以上
- [ ] セキュリティスキャン合格
- [ ] パフォーマンステスト合格
- [ ] レビュー承認済み
- [ ] マイグレーションスクリプト確認
- [ ] 環境変数設定確認
- [ ] ロールバックプラン準備

## 自動化タスク

### 1. コード品質チェック
- **ESLint**: JavaScriptコードの品質
- **Black**: Pythonコードのフォーマット
- **isort**: Pythonインポートの整理
- **TypeScript**: 型チェック
- **mypy**: Python型チェック

### 2. セキュリティチェック
- **npm audit**: Node.js依存関係の脆弱性
- **safety**: Python依存関係の脆弱性
- **bandit**: Pythonコードのセキュリティ
- **OWASP依存関係チェック**

### 3. パフォーマンステスト
- **Lighthouse CI**: フロントエンドパフォーマンス
- **API レスポンステスト**: バックエンドパフォーマンス
- **負荷テスト**: スケーラビリティ確認

## モニタリングとアラート

### デプロイ後の自動チェック

```yaml
- name: Post-deployment checks
  run: |
    # ヘルスチェック
    curl -f https://api.aica-sys.com/health || exit 1
    
    # スモークテスト
    npm run test:smoke
    
    # パフォーマンスチェック
    npm run test:performance
```

### アラート設定

- **デプロイ失敗**: Slack通知
- **テスト失敗**: GitHub通知 + Slack
- **セキュリティ問題**: 即座の通知

## ロールバック手順

### 自動ロールバック

```yaml
- name: Automatic rollback on failure
  if: failure()
  run: |
    # 前のバージョンに戻す
    kubectl rollout undo deployment/aica-sys-backend
```

### 手動ロールバック

```bash
# Vercel
vercel rollback

# Kubernetes
kubectl rollout undo deployment/aica-sys-backend

# Docker
docker-compose up -d --scale backend=0
docker-compose up -d --scale backend=3 --force-recreate
```

## 実装手順

1. **GitHub Actionsワークフローファイルの作成**
2. **環境変数とシークレットの設定**
3. **テストスクリプトの整備**
4. **デプロイスクリプトの作成**
5. **ロールバック手順の確立**
6. **ドキュメントの整備**
7. **パイプラインのテスト**

## 期待される効果

- **デプロイ時間**: 手動30分 → 自動10分
- **デプロイ頻度**: 週1回 → 日次
- **エラー検出**: デプロイ後 → デプロイ前
- **コード品質**: 向上（自動チェック）
- **開発速度**: 30%向上

## 次のステップ

Phase 8-1の実装を開始します。
