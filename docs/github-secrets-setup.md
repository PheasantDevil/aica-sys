# GitHub Secrets 設定ガイド

GitHub Actions でデプロイを自動化するために、以下の Secrets を GitHub リポジトリに設定する必要があります。

## 1. リポジトリの Secrets 設定にアクセス

1. GitHub リポジトリのページにアクセス
2. **Settings** タブをクリック
3. 左サイドバーの **Secrets and variables** → **Actions** をクリック
4. **New repository secret** ボタンをクリック

## 2. 必要な Secrets

### 2.1 フロントエンド用 Secrets

| Secret 名                            | 説明                                  | 例                            |
| ------------------------------------ | ------------------------------------- | ----------------------------- |
| `NEXT_PUBLIC_GA_ID`                  | Google Analytics 測定 ID              | `G-EQWV08KBKM`                |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe 公開キー                       | `pk_test_...`                 |
| `NEXTAUTH_SECRET`                    | NextAuth.js シークレット              | ランダムな 32 文字            |
| `GOOGLE_CLIENT_ID`                   | Google OAuth クライアント ID          | `489836083648-...`            |
| `GOOGLE_CLIENT_SECRET`               | Google OAuth クライアントシークレット | `GOCSPX-...`                  |
| `STRIPE_SECRET_KEY`                  | Stripe シークレットキー               | `sk_test_...`                 |
| `STRIPE_WEBHOOK_SECRET`              | Stripe Webhook シークレット           | `whsec_...`                   |
| `RESEND_API_KEY`                     | Resend API キー                       | `re_...`                      |
| `NEXT_PUBLIC_BASE_URL`               | 本番環境のベース URL                  | `https://aica-sys.vercel.app` |

### 2.2 Vercel 用 Secrets

| Secret 名      | 説明                | 取得方法                             |
| -------------- | ------------------- | ------------------------------------ |
| `VERCEL_TOKEN` | Vercel API トークン | Vercel Dashboard → Settings → Tokens |

### 2.3 バックエンド用 Secrets

| Secret 名           | 説明                         | 例                      |
| ------------------- | ---------------------------- | ----------------------- |
| `GOOGLE_AI_API_KEY` | Google AI Studio API キー    | `AIza...`               |
| `OPENAI_API_KEY`    | OpenAI API キー              | `sk-...`                |
| `GITHUB_TOKEN`      | GitHub Personal Access Token | `ghp_...`               |
| `DATABASE_URL`      | データベース接続文字列       | `postgresql://...`      |
| `REDIS_URL`         | Redis 接続文字列             | `redis://...`           |
| `QDRANT_URL`        | Qdrant 接続 URL              | `http://localhost:6333` |
| `QDRANT_API_KEY`    | Qdrant API キー              | `your-qdrant-key`       |
| `JWT_SECRET_KEY`    | JWT 署名用シークレット       | ランダムな 32 文字      |
| `ENCRYPTION_KEY`    | データ暗号化用キー           | ランダムな 32 文字      |

### 2.4 GCP 用 Secrets

| Secret 名        | 説明                       | 取得方法                |
| ---------------- | -------------------------- | ----------------------- |
| `GCP_SA_KEY`     | GCP サービスアカウントキー | JSON 形式のキーファイル |
| `GCP_PROJECT_ID` | GCP プロジェクト ID        | `your-project-id`       |

### 2.5 ソーシャル連携用 Secrets (オプション)

| Secret 名                | 説明                              | 例         |
| ------------------------ | --------------------------------- | ---------- |
| `TWITTER_API_KEY`        | Twitter API キー                  | `your-...` |
| `TWITTER_API_SECRET`     | Twitter API シークレット          | `your-...` |
| `LINKEDIN_CLIENT_ID`     | LinkedIn クライアント ID          | `your-...` |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn クライアントシークレット | `your-...` |

### 2.6 セキュリティ用 Secrets (オプション)

| Secret 名    | 説明              | 取得方法                          |
| ------------ | ----------------- | --------------------------------- |
| `SNYK_TOKEN` | Snyk API トークン | Snyk Dashboard → Account Settings |

## 3. Vercel API トークンの取得

1. [Vercel Dashboard](https://vercel.com/dashboard) にログイン
2. 右上のアバターをクリック → **Settings**
3. 左サイドバーの **Tokens** をクリック
4. **Create Token** をクリック
5. トークン名を入力（例：`aica-sys-github-actions`）
6. スコープを選択（**Full Account** 推奨）
7. **Create** をクリック
8. 生成されたトークンをコピーして `VERCEL_TOKEN` として設定

## 4. GCP サービスアカウントキーの取得

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを選択
3. **IAM & Admin** → **Service Accounts** をクリック
4. **Create Service Account** をクリック
5. サービスアカウント名を入力（例：`aica-sys-github-actions`）
6. ロールを選択：
   - **Cloud Functions Admin**
   - **Service Account User**
   - **Storage Admin**
7. **Create and Continue** をクリック
8. **Keys** タブをクリック
9. **Add Key** → **Create new key** → **JSON** を選択
10. ダウンロードされた JSON ファイルの内容をコピーして `GCP_SA_KEY` として設定

## 5. GitHub Personal Access Token の取得

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token** → **Generate new token (classic)** をクリック
3. トークン名を入力（例：`aica-sys-backend`）
4. スコープを選択：
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
5. **Generate token** をクリック
6. 生成されたトークンをコピーして `GITHUB_TOKEN` として設定

## 6. 設定確認

すべての Secrets を設定したら、以下のコマンドで確認できます：

```bash
# リポジトリのSecrets一覧を確認
gh secret list

# 特定のSecretの存在確認
gh secret get SECRET_NAME
```

## 7. 注意事項

- Secrets は暗号化されて保存されます
- 一度設定した Secret の値は表示できません
- 更新する場合は、新しい値で上書きしてください
- 不要になった Secret は削除することを推奨します

## 8. トラブルシューティング

### よくある問題

1. **Vercel デプロイが失敗する**
   - `VERCEL_TOKEN` が正しく設定されているか確認
   - Vercel プロジェクトが正しくリンクされているか確認

2. **GCP デプロイが失敗する**
   - `GCP_SA_KEY` の JSON 形式が正しいか確認
   - サービスアカウントに必要な権限があるか確認

3. **テストが失敗する**
   - 必要な環境変数がすべて設定されているか確認
   - テスト用の API キーが有効か確認
