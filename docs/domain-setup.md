# ドメイン設定ガイド

## 無料ドメインの選択肢

### 1. Vercel 無料ドメイン（推奨）

**メリット:**

- 完全無料
- SSL 証明書自動発行
- 高速 CDN
- 簡単設定

**設定手順:**

1. Vercel にデプロイ後、プロジェクト設定でドメインを追加
2. 形式: `aica-sys.vercel.app` または `aica-sys-xxx.vercel.app`
3. カスタムドメインも後から追加可能

### 2. GitHub Pages 無料ドメイン

**メリット:**

- 完全無料
- GitHub と連携

**設定手順:**

1. リポジトリ設定で GitHub Pages を有効化
2. 形式: `username.github.io/aica-sys`

### 3. Netlify 無料ドメイン

**メリット:**

- 完全無料
- 簡単設定

**設定手順:**

1. Netlify にデプロイ後、ドメイン設定
2. 形式: `aica-sys.netlify.app`

## 推奨設定

### Vercel 無料ドメインを使用

**ドメイン例:**

- `aica-sys.vercel.app`
- `aica-sys-dev.vercel.app`

**設定する URL:**

```
アプリケーションのホームページ: https://aica-sys.vercel.app
プライバシーポリシー: https://aica-sys.vercel.app/privacy-policy.html
利用規約: https://aica-sys.vercel.app/terms-of-service.html
```

**Authorized redirect URIs:**

```
http://localhost:3000/api/auth/callback/google
https://aica-sys.vercel.app/api/auth/callback/google
```

## 本番環境での設定

### 1. Vercel デプロイ

```bash
# Vercel CLI インストール
npm i -g vercel

# デプロイ
cd frontend
vercel --prod
```

### 2. ドメイン設定

1. Vercel ダッシュボードでプロジェクトを選択
2. 「Settings」→「Domains」
3. ドメインを追加: `aica-sys.vercel.app`

### 3. 環境変数更新

```env
NEXTAUTH_URL=https://aica-sys.vercel.app
NEXT_PUBLIC_BASE_URL=https://aica-sys.vercel.app
```

## カスタムドメイン（将来）

### 無料ドメインサービス

- **Freenom**: `.tk`, `.ml`, `.ga`, `.cf` ドメイン
- **No-IP**: 動的 DNS サービス
- **DuckDNS**: 無料 DNS サービス

### 有料ドメイン（推奨）

- **お名前.com**: 国内最安値
- **GoDaddy**: 国際的サービス
- **Cloudflare**: セキュリティ機能付き

## 設定完了後の確認

### 1. ドメインアクセステスト

```bash
curl -I https://aica-sys.vercel.app
```

### 2. SSL 証明書確認

```bash
openssl s_client -connect aica-sys.vercel.app:443 -servername aica-sys.vercel.app
```

### 3. OAuth 設定確認

- Google Cloud Console でリダイレクト URI を更新
- 認証フローのテスト
