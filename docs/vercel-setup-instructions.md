# Vercel セットアップ手順

## 問題と解決策

### 問題
```
Error: No Next.js version detected. Make sure your package.json has "next" in either "dependencies" or "devDependencies".
```

### 原因
- Vercelがルートディレクトリの`package.json`を見ている
- Next.jsは`frontend/package.json`にある
- Root Directoryの設定が必要

### 解決策

Vercel Dashboardで**Root Directory**を設定する。

---

## Vercel Dashboard 設定手順

### 1. プロジェクト設定を開く

1. Vercel Dashboard → プロジェクト選択
2. "Settings" タブをクリック
3. "General" セクション

### 2. Root Directory 設定

```
Root Directory: frontend
```

**変更後**: "Save" をクリック

### 3. Framework Preset（自動検出されるはず）

```
Framework Preset: Next.js
```

### 4. Build & Development Settings

#### Build Command（自動検出）
```
npm run build
```

#### Output Directory（自動検出）
```
.next
```

#### Install Command（自動検出）
```
npm install
```

**これらは自動で検出されるため、通常は変更不要**

---

## 環境変数設定

### Vercel Dashboard → Settings → Environment Variables

#### Production
```bash
NEXTAUTH_URL=https://aica-sys.vercel.app
NEXT_PUBLIC_BASE_URL=https://aica-sys.vercel.app
NEXT_PUBLIC_API_URL=https://aica-sys-backend.onrender.com
ENVIRONMENT=production
NEXTAUTH_SECRET=（シークレット生成）
GOOGLE_CLIENT_ID=（Google OAuth設定）
GOOGLE_CLIENT_SECRET=（Google OAuth設定）
```

#### Preview（オプション）
```bash
NEXTAUTH_URL=https://aica-sys-git-[branch].vercel.app
NEXT_PUBLIC_API_URL=https://aica-sys-backend.onrender.com
ENVIRONMENT=preview
```

---

## 再デプロイ

### 方法1: Git Push（推奨）
```bash
git push origin main
```
→ 自動デプロイ

### 方法2: Vercel Dashboard
1. Deployments タブ
2. 最新デプロイの "..." メニュー
3. "Redeploy"

### 方法3: Vercel CLI
```bash
cd frontend
vercel --prod
```

---

## vercel.json の役割

### 最小構成（推奨）

```json
{
  "version": 2,
  "env": {
    "NEXTAUTH_URL": "https://aica-sys.vercel.app",
    "NEXT_PUBLIC_BASE_URL": "https://aica-sys.vercel.app",
    "NEXT_PUBLIC_API_URL": "https://aica-sys-backend.onrender.com",
    "ENVIRONMENT": "production"
  }
}
```

**Root Directoryの設定はDashboardで行う**のが推奨。

---

## トラブルシューティング

### エラー: "No Next.js version detected"

**原因**: Root Directoryが未設定
**解決**: Dashboard → Settings → Root Directory: `frontend`

### エラー: "Module not found"

**原因**: 依存関係のインストール失敗
**解決**: `frontend/package.json`と`package-lock.json`を確認

### エラー: "Build timeout"

**原因**: ビルド時間が制限を超過
**解決**: 
- 不要な依存関係を削除
- `.vercelignore`で不要ファイルを除外（実装済み）

---

## 確認方法

### ビルド成功
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages
✓ Finalizing page optimization

Route (app)                 Size     First Load JS
┌ ○ /                      [size]   [size]
└ ○ /api/auth/[...nextauth] ...
```

### デプロイ成功
```
https://aica-sys.vercel.app
Status: Ready
```

---

## まとめ

### 必須設定
1. ✅ **Root Directory**: `frontend`（Dashboard設定）
2. ✅ **環境変数**: NEXTAUTH_URL等（Dashboard設定）
3. ✅ **vercel.json**: 最小構成（env設定のみ）

### 自動検出される
- Framework: Next.js
- Build Command
- Output Directory
- Install Command

**Root Directory設定後、すぐにデプロイ成功するはずです** ✅

