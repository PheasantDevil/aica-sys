# Groq API設定ガイド

## 概要

AICA-SySは、AI駆動型コンテンツ生成にGroq APIを使用しています。Groqは無料で高速なLlama 3.3 70Bモデルを提供しており、OpenAIより高いパフォーマンスを実現できます。

## Groq APIの利点

| 項目       | Groq (Llama 3.3 70B) | OpenAI (GPT-4)   |
| ---------- | -------------------- | ---------------- |
| **コスト** | 完全無料             | $10-30/1M tokens |
| **速度**   | 10倍高速             | 標準             |
| **無料枠** | 14,400 requests/日   | 限定的           |
| **品質**   | 高品質               | 最高品質         |

## 1. Groq APIキーの取得

### ステップ1: アカウント作成

1. [Groq Console](https://console.groq.com/)にアクセス
2. 「Sign Up」でアカウント作成
   - GoogleアカウントまたはGitHubアカウントで登録可能
3. メール認証を完了

### ステップ2: APIキー生成

1. ログイン後、左サイドバーから「API Keys」を選択
2. 「Create API Key」ボタンをクリック
3. キー名を入力（例: "aica-sys-production"）
4. 生成されたAPIキーをコピー
   - **重要**: APIキーは一度しか表示されないので、必ず安全な場所に保存

## 2. ローカル開発環境設定

### .env.localファイル作成

```bash
cd /Users/Work/aica-sys
cp backend/env.example backend/.env.local
```

### APIキーを設定

`backend/.env.local`を編集：

```bash
# AI Services (Groq - 完全無料)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 動作確認

```bash
cd backend
source venv/bin/activate
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.local')
print('GROQ_API_KEY:', os.getenv('GROQ_API_KEY')[:20] + '...')
"
```

## 3. GitHub Secrets設定

### GitHub Actions用環境変数

1. GitHubリポジトリページにアクセス
2. 「Settings」→「Secrets and variables」→「Actions」
3. 「New repository secret」をクリック
4. 以下のシークレットを追加：

```
Name: GROQ_API_KEY
Value: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 確認方法

GitHub Actionsワークフローを手動トリガーして確認：

```bash
# GitHub CLI使用
gh workflow run daily-articles.yml

# または、GitHub UIから
# Actions → Daily Article Generation → Run workflow
```

## 4. Render環境変数設定

### Render Dashboard設定

1. [Render Dashboard](https://dashboard.render.com/)にログイン
2. AICA-SySバックエンドサービスを選択
3. 「Environment」タブを開く
4. 「Add Environment Variable」をクリック
5. 以下を追加：

```
Key: GROQ_API_KEY
Value: gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

6. 「Save Changes」をクリック
7. サービスが自動的に再デプロイされます

## 5. Vercel環境変数設定（フロントエンド）

フロントエンドではGroq APIを直接使用しませんが、バックエンドAPI経由でアクセスします。

### Vercel Dashboard設定

1. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
2. AICA-SySプロジェクトを選択
3. 「Settings」→「Environment Variables」
4. 必要に応じて以下を追加（バックエンドURL）：

```
Name: NEXT_PUBLIC_API_URL
Value: https://aica-sys-backend.onrender.com
```

## 6. APIレート制限

### Groq無料枠の制限

```
- リクエスト数: 14,400 requests/日
- トークン数: 無制限（モデルによる）
- 同時接続: 10 requests/秒
```

### レート制限対策

`backend/utils/ai_client.py`には自動リトライ機能が実装されています：

```python
# 自動リトライ（エラー時）
try:
    response = await self.ai_client.generate_content(request)
except Exception as e:
    logger.error(f"Groq API error: {e}")
    # フォールバック処理
```

## 7. トラブルシューティング

### エラー: "Invalid API Key"

- APIキーが正しくコピーされているか確認
- 環境変数名が `GROQ_API_KEY` になっているか確認
- `.env.local`ファイルの場所が正しいか確認

### エラー: "Rate limit exceeded"

- 1日14,400リクエストを超えていないか確認
- 複数環境で同じAPIキーを使用していないか確認
- 必要に応じて複数のAPIキーを取得

### エラー: "Model not found"

- モデル名が `llama-3.3-70b-versatile` になっているか確認
- 最新のモデル名は[Groq Models](https://console.groq.com/docs/models)で確認

## 8. セキュリティベストプラクティス

### APIキー管理

1. **絶対にコミットしない**

   ```bash
   # .gitignoreに含まれていることを確認
   .env
   .env.local
   .env.*.local
   ```

2. **環境変数で管理**
   - ローカル: `.env.local`
   - GitHub Actions: Secrets
   - Render: Environment Variables
   - Vercel: Environment Variables

3. **定期的な更新**
   - APIキーは3-6ヶ月ごとに更新推奨
   - 古いキーは削除

4. **権限の最小化**
   - 必要最小限の権限のみ付与
   - 本番用と開発用でキーを分ける

## 9. モニタリング

### 使用状況確認

Groq Consoleで使用状況を確認：

1. [Groq Console](https://console.groq.com/)にログイン
2. 「Usage」タブで確認
   - 日次リクエスト数
   - トークン使用量
   - エラー率

### アラート設定

```python
# backend/services/content_automation_service.py
# 使用量が80%を超えたらログ出力
if daily_requests > 11520:  # 14400 * 0.8
    logger.warning("Groq API usage > 80%")
```

## 10. 次のステップ

✅ Groq API設定完了後：

1. データベースマイグレーション実行

   ```bash
   cd backend
   source venv/bin/activate
   alembic revision --autogenerate -m "Add automated content tables"
   alembic upgrade head
   ```

2. 記事生成テスト

   ```bash
   cd /Users/Work/aica-sys
   source backend/venv/bin/activate
   python3 scripts/generate_daily_article.py
   ```

3. GitHub Actionsで自動化確認
   ```bash
   gh workflow run daily-articles.yml
   ```

## 参考リンク

- [Groq公式ドキュメント](https://console.groq.com/docs)
- [Groq APIリファレンス](https://console.groq.com/docs/api-reference)
- [Llama 3.3モデル詳細](https://console.groq.com/docs/models)
- [レート制限ガイド](https://console.groq.com/docs/rate-limits)
