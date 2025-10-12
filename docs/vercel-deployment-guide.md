# Vercel デプロイメントガイド

## 構成

AICA-SySは以下の構成でデプロイされます：

### フロントエンド: Vercel
- **フレームワーク**: Next.js
- **ディレクトリ**: `frontend/`
- **URL**: https://aica-sys.vercel.app

### バックエンド: 別途デプロイ
- **フレームワーク**: FastAPI
- **ディレクトリ**: `backend/`
- **推奨**: Google Cloud Run / AWS Lambda / Railway
- **URL**: https://api.aica-sys.com（設定必要）

## Vercel設定

### vercel.json
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs"
}
```

### 環境変数（Vercel Dashboard）
```
NEXTAUTH_URL=https://aica-sys.vercel.app
NEXT_PUBLIC_BASE_URL=https://aica-sys.vercel.app
NEXT_PUBLIC_API_URL=https://api.aica-sys.com
ENVIRONMENT=production
NEXTAUTH_SECRET=（シークレット）
GOOGLE_CLIENT_ID=（Google OAuth）
GOOGLE_CLIENT_SECRET=（Google OAuth）
```

## バックエンドデプロイオプション

### オプション1: Google Cloud Run（推奨）
```bash
# Dockerビルド
docker build -t gcr.io/PROJECT_ID/aica-sys-backend backend/

# プッシュ
docker push gcr.io/PROJECT_ID/aica-sys-backend

# デプロイ
gcloud run deploy aica-sys-backend \
  --image gcr.io/PROJECT_ID/aica-sys-backend \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

### オプション2: Railway
1. Railwayアカウント作成
2. GitHubリポジトリ接続
3. `backend/`ディレクトリを選択
4. 環境変数設定
5. 自動デプロイ

### オプション3: Render
1. Renderアカウント作成
2. Web Service作成
3. Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## トラブルシューティング

### エラー: "pattern doesn't match any Serverless Functions"
**原因**: `functions`設定が不正
**解決**: `vercel.json`から`functions`を削除（修正済み）

### エラー: Database connection failed
**原因**: Supabase一時停止 or 環境変数未設定
**解決**: 
```bash
make check-db  # ローカルで確認
```

### エラー: Build timeout
**原因**: ビルド時間が制限を超過
**解決**: `vercel.json`に`buildCommand`を最適化

## デプロイフロー

### 自動デプロイ
```
git push origin main
  ↓
GitHub Actions（frontend-ci-cd.yml）
  ↓
Vercel自動デプロイ
  ↓
https://aica-sys.vercel.app
```

### 手動デプロイ
```bash
cd frontend
vercel --prod
```

## モニタリング

### Vercel Dashboard
- Speed Insights（Phase 11-1）
- Web Analytics
- Runtime Logs
- Build Logs

### ローカル確認
```bash
make check-db    # DB接続確認
make db-status   # DB状態確認
```

