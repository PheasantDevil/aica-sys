# Render バックエンドデプロイガイド

## 概要

AICA-SySバックエンド（FastAPI）をRender Freeプランでデプロイする手順。

## 採用理由

### ✅ 完全無料

- Render Free tier: $0/月
- Vercel Hobby: $0/月
- **合計: $0/月**

### ✅ 復旧が簡単

- デプロイ履歴から1クリックでロールバック
- 過去30日分のデプロイ履歴保持

### ✅ 保守管理が簡単

- GitHubリポジトリ接続で自動デプロイ
- GUIで環境変数管理
- ログ・メトリクス統合

## デプロイ手順

### Step 1: Renderアカウント作成

1. https://render.com にアクセス
2. "Get Started for Free" をクリック
3. GitHubアカウントで認証

### Step 2: Web Service作成

1. Dashboard → "New +"
2. "Web Service" を選択
3. GitHubリポジトリを接続: `PheasantDevil/aica-sys`
4. "Connect" をクリック

### Step 3: サービス設定

#### 基本設定

```
Name: aica-sys-backend
Region: Singapore (or Tokyo if available)
Branch: main
Root Directory: backend
Runtime: Python 3
```

#### Build設定

```
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### プラン

```
Instance Type: Free
```

### Step 4: 環境変数設定

Render Dashboard → Environment で以下を設定：

#### 必須

```bash
PYTHON_VERSION=3.13.0
DATABASE_URL=sqlite:///./aica_sys.db
ENVIRONMENT=production
CORS_ORIGINS=https://aica-sys.vercel.app
```

#### OpenAI（必要に応じて）

```bash
OPENAI_API_KEY=sk-...
```

#### 認証（必要に応じて）

```bash
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
NEXTAUTH_SECRET=...
```

#### Stripe（必要に応じて）

```bash
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...
```

### Step 5: デプロイ実行

1. "Create Web Service" をクリック
2. ビルドが自動開始
3. ログでビルド進捗を確認
4. デプロイ完了を待つ（5-10分）

### Step 6: URL確認

デプロイ完了後、以下のURLが発行されます：

```
https://aica-sys-backend.onrender.com
```

ヘルスチェック:

```bash
curl https://aica-sys-backend.onrender.com/health
```

### Step 7: Vercel環境変数更新

Vercel Dashboard → Settings → Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://aica-sys-backend.onrender.com
```

保存後、Vercelで再デプロイ。

---

## 自動デプロイ設定

### GitHub連携（デフォルト有効）

```
git push origin main
  ↓
GitHub webhook
  ↓
Render自動ビルド
  ↓
自動デプロイ
```

### render.yaml（オプション）

リポジトリルートに`render.yaml`を配置すると、設定をコード化できます。

---

## ロールバック手順

### Renderダッシュボードから

1. Dashboard → aica-sys-backend を選択
2. "Events" タブをクリック
3. 過去のデプロイを選択
4. "Rollback to this version" をクリック

**所要時間**: 約30秒 ✅

### CLI から（オプション）

```bash
# Render CLI インストール
brew install render

# ロールバック
render services rollback aica-sys-backend --to-deploy <deploy-id>
```

---

## モニタリング

### Renderダッシュボード

- **Metrics**: CPU、メモリ、リクエスト数
- **Logs**: リアルタイムログストリーミング
- **Events**: デプロイ履歴、ステータス変更

### ヘルスチェック

```bash
# ステータス確認
curl https://aica-sys-backend.onrender.com/health

# メトリクス確認
curl https://aica-sys-backend.onrender.com/metrics
```

### アラート設定

Render Dashboard → Notifications:

- デプロイ失敗時
- サービスダウン時
- メモリ制限到達時

---

## トラブルシューティング

### ビルド失敗

**原因**: 依存関係エラー
**確認**:

```bash
# ローカルで確認
cd backend
pip install -r requirements.txt
```

### 起動失敗

**原因**: 環境変数未設定、ポート設定ミス
**確認**:

- 環境変数が正しく設定されているか
- `$PORT`を使用しているか

### スリープからの復帰が遅い

**原因**: Render Freeの仕様
**対策**:

1. $7/月のStarterプランにアップグレード
2. または、ヘルスチェックCronで定期的にping（非推奨）

### データベース接続エラー

**原因**: DATABASE_URL設定ミス
**確認**:

```bash
make check-db  # ローカルで接続確認
```

---

## スケールアップパス

### Free → Starter（$7/月）

**タイミング**:

- スリープが問題になった時
- トラフィックが増えた時

**変更点**:

- スリープなし
- より高性能（512MB、0.5 CPU）

### Starter → Professional（$25/月）

**タイミング**:

- さらなるパフォーマンスが必要な時

**変更点**:

- 2GB RAM、1 CPU
- 高速起動

---

## PostgreSQL移行（将来的）

### Render PostgreSQL

**コスト**: $7/月（256MB）

**手順**:

1. Dashboard → "New +" → "PostgreSQL"
2. 自動で`DATABASE_URL`が設定される
3. バックエンドで自動認識

### Neon PostgreSQL（推奨）

**コスト**: $0（無料枠512MB）

**手順**:

1. https://neon.tech でアカウント作成
2. データベース作成
3. 接続文字列をRender環境変数に設定

---

## まとめ

### 現在の構成（Phase 11）

```
Frontend: Vercel Hobby ($0)
Backend: Render Free ($0)
Database: SQLite（ファイルベース）

合計: $0/月
```

### 成長時の構成（Phase 12+）

```
Frontend: Vercel Hobby ($0)
Backend: Render Starter ($7)
Database: Neon PostgreSQL ($0)

合計: $7/月
```

### 本格運用時

```
Frontend: Vercel Pro ($20)
Backend: Cloud Run ($10-50)
Database: Cloud SQL ($10-30)

合計: $40-100/月
```

**段階的にスケール可能** ✅
