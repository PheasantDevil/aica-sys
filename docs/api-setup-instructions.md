# 🔧 API 設定手順 - 取得済みキー

## 取得済み API キー

以下の API キーを取得済みです：

- **GOOGLE_AI_API_KEY**: `AIzaSyDE1_kHCNUlGItZ4CxuWH9yxRFIw___pkw` (実際の値)
- **OPENAI_API_KEY**: `sk-proj-***` (実際の値は設定時に使用)
- **GITHUBPA_TOKEN**: `ghp_***` (実際の値は設定時に使用、GitHub Secret 命名制約対応)

## 設定手順

### 1. ローカル環境の設定

#### .env ファイルの編集

```bash
# エディタで .env ファイルを開く
nano .env
# または
code .env
```

#### 以下の行を変更

```bash
# 変更前
GOOGLE_AI_API_KEY=your_google_ai_key_here
OPENAI_API_KEY=your_openai_key_here
GITHUB_TOKEN=your_github_token_here

# 変更後
GOOGLE_AI_API_KEY=AIzaSyDE1_kHCNUlGItZ4CxuWH9yxRFIw___pkw
OPENAI_API_KEY=sk-proj-*** (実際の値に置き換え)
GITHUB_TOKEN=ghp_*** (実際の値に置き換え)
```

### 2. GitHub Secrets の設定

#### リポジトリの設定画面にアクセス

- GitHub リポジトリ → Settings → Secrets and variables → Actions

#### 以下の Secrets を追加

| Name                | Value                                                                                                                                                                  | 説明                      |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| `GOOGLE_AI_API_KEY` | `AIzaSyDE1_kHCNUlGItZ4CxuWH9yxRFIw___pkw` | Google AI API             |
| `OPENAI_API_KEY`    | `sk-proj-***` (実際の値に置き換え)         | OpenAI API                |
| `GITHUBPA_TOKEN`    | `ghp_***` (実際の値に置き換え)             | GitHub API (命名制約対応) |
| `DATABASE_URL`      | `sqlite:///./aica_sys.db`                                                                                                                                              | データベース              |
| `JWT_SECRET_KEY`    | `lSruCv7yiOnixpKnW36V82uZ76gbjY6GB02J/fOn4xc=`                                                                                                                         | JWT 認証                  |
| `ENCRYPTION_KEY`    | `kOafjcTCRw8pH3ODidAZiCqOGhPgUzfmbxfiycGcEs0=`                                                                                                                         | データ暗号化              |
| `NEXTAUTH_SECRET`   | `UJizZfOoGEEOgyHymka0/gzKLKE0Ia730pUhBUfKx6Q=`                                                                                                                         | NextAuth.js               |

### 3. 設定確認

#### API 接続テスト

```bash
# 取得したAPIキーでテスト
./scripts/test-apis.sh
```

#### 設定確認

```bash
# 全体的な設定確認
./scripts/check-config.sh
```

### 4. 起動テスト

#### バックエンド起動

```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### フロントエンド起動（別ターミナル）

```bash
cd frontend
npm run dev
```

#### アクセス確認

- フロントエンド: http://localhost:3000
- バックエンド API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

### 5. 初回データ収集テスト

#### API エンドポイント経由

```bash
# データ収集を開始
curl -X POST "http://localhost:8000/ai/collect"

# 分析を実行
curl -X POST "http://localhost:8000/ai/analyze"

# コンテンツ生成
curl -X POST "http://localhost:8000/ai/generate?content_type=article"
```

#### 統計情報確認

```bash
# AI統計情報を取得
curl "http://localhost:8000/ai/stats"
```

## トラブルシューティング

### よくある問題

1. **依存関係エラー**

   ```bash
   cd backend
   pip3 install -r requirements.txt
   ```

2. **API 接続エラー**

   - API キーが正しく設定されているか確認
   - ネットワーク接続を確認

3. **データベースエラー**

   ```bash
   cd backend
   python3 -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

4. **ポート競合**
   - 別のポートを使用: `uvicorn main:app --reload --port 8001`

### ログ確認

```bash
# バックエンドログ
cd backend && python3 main.py

# フロントエンドログ
cd frontend && npm run dev
```

## 次のステップ

設定完了後：

1. 初回データ収集の実行
2. AI 分析のテスト
3. コンテンツ生成の確認
4. 本番環境へのデプロイ

すべての設定が完了すると、AICA-SyS の本格運用を開始できます！
