# GitHub Secrets 設定ガイド

GitHub Actionsでデプロイを自動化するために、以下のSecretsをGitHubリポジトリに設定する必要があります。

## 1. リポジトリのSecrets設定にアクセス

1. GitHubリポジトリのページにアクセス
2. **Settings** タブをクリック
3. 左サイドバーの **Secrets and variables** → **Actions** をクリック
4. **New repository secret** ボタンをクリック

## 2. 必要なSecrets

### 2.1 フロントエンド用Secrets

| Secret名 | 説明 | 例 |
|---------|------|-----|
| `NEXT_PUBLIC_GA_ID` | Google Analytics 測定ID | `G-EQWV08KBKM` |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Stripe公開キー | `pk_test_...` |
| `NEXTAUTH_SECRET` | NextAuth.js シークレット | ランダムな32文字 |
| `GOOGLE_CLIENT_ID` | Google OAuth クライアントID | `489836083648-...` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth クライアントシークレット | `GOCSPX-...` |
| `STRIPE_SECRET_KEY` | Stripe シークレットキー | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe Webhook シークレット | `whsec_...` |
| `RESEND_API_KEY` | Resend API キー | `re_...` |
| `NEXT_PUBLIC_BASE_URL` | 本番環境のベースURL | `https://aica-sys.vercel.app` |

### 2.2 Vercel用Secrets

| Secret名 | 説明 | 取得方法 |
|---------|------|----------|
| `VERCEL_TOKEN` | Vercel API トークン | Vercel Dashboard → Settings → Tokens |

### 2.3 バックエンド用Secrets

| Secret名 | 説明 | 例 |
|---------|------|-----|
| `GOOGLE_AI_API_KEY` | Google AI Studio API キー | `AIza...` |
| `OPENAI_API_KEY` | OpenAI API キー | `sk-...` |
| `GITHUB_TOKEN` | GitHub Personal Access Token | `ghp_...` |

### 2.4 GCP用Secrets

| Secret名 | 説明 | 取得方法 |
|---------|------|----------|
| `GCP_SA_KEY` | GCP サービスアカウントキー | JSON形式のキーファイル |
| `GCP_PROJECT_ID` | GCP プロジェクトID | `your-project-id` |

### 2.5 セキュリティ用Secrets

| Secret名 | 説明 | 取得方法 |
|---------|------|----------|
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
10. ダウンロードされたJSONファイルの内容をコピーして `GCP_SA_KEY` として設定

## 5. GitHub Personal Access Tokenの取得

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token** → **Generate new token (classic)** をクリック
3. トークン名を入力（例：`aica-sys-backend`）
4. スコープを選択：
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
5. **Generate token** をクリック
6. 生成されたトークンをコピーして `GITHUB_TOKEN` として設定

## 6. 設定確認

すべてのSecretsを設定したら、以下のコマンドで確認できます：

```bash
# リポジトリのSecrets一覧を確認
gh secret list

# 特定のSecretの存在確認
gh secret get SECRET_NAME
```

## 7. 注意事項

- Secretsは暗号化されて保存されます
- 一度設定したSecretの値は表示できません
- 更新する場合は、新しい値で上書きしてください
- 不要になったSecretは削除することを推奨します

## 8. トラブルシューティング

### よくある問題

1. **Vercelデプロイが失敗する**
   - `VERCEL_TOKEN` が正しく設定されているか確認
   - Vercelプロジェクトが正しくリンクされているか確認

2. **GCPデプロイが失敗する**
   - `GCP_SA_KEY` のJSON形式が正しいか確認
   - サービスアカウントに必要な権限があるか確認

3. **テストが失敗する**
   - 必要な環境変数がすべて設定されているか確認
   - テスト用のAPIキーが有効か確認
