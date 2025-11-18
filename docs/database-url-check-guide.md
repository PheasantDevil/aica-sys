# データベース URL 確認方法ガイド

## 1. GitHub Secrets での確認方法

### GitHub リポジトリの設定から確認

1. GitHub リポジトリにアクセス
2. **Settings** → **Secrets and variables** → **Actions** を開く
3. `DATABASE_URL` を検索して確認

### GitHub CLI で確認（値は表示されません）

```bash
gh secret list
```

## 2. ローカル環境での確認方法

### 環境変数の確認

```bash
# 現在の環境変数を確認
echo $DATABASE_URL

# .envファイルから確認（存在する場合）
cat backend/.env | grep DATABASE_URL
```

### Python スクリプトで確認

```python
import os
from pathlib import Path

# 環境変数から取得
database_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {database_url}")

# デフォルト値の確認
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'aica_sys.db').as_posix()}"
print(f"Default SQLite URL: {DEFAULT_SQLITE_URL}")
```

## 3. データベース接続の確認方法

### Python スクリプトで接続テスト

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path('backend')))

from database import SessionLocal, engine

# 接続テスト
try:
    db = SessionLocal()
    db.execute("SELECT 1")
    db.close()
    print("✅ Database connection OK")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

### コマンドラインで確認

```bash
cd backend
python3 -c "
from pathlib import Path
import sys
import os
sys.path.insert(0, str(Path('.')))

# 環境変数を確認
db_url = os.getenv('DATABASE_URL', 'Not set')
print(f'DATABASE_URL: {db_url}')

# 接続テスト
try:
    from database import SessionLocal
    db = SessionLocal()
    db.close()
    print('✅ Connection successful')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

## 4. データベースタイプの判定

### コード内での確認

```python
from backend.database import DATABASE_URL, is_sqlite, is_postgresql

print(f"Database URL: {DATABASE_URL}")
print(f"Is SQLite: {is_sqlite}")
print(f"Is PostgreSQL: {is_postgresql}")
```

## 5. デフォルト値の確認

### デフォルトの SQLite パス

- デフォルト: `sqlite:///backend/aica_sys.db`
- `DATABASE_URL`が設定されていない場合、自動的にこのパスが使用されます

### 確認方法

```bash
# デフォルトのSQLiteファイルの存在確認
ls -la backend/aica_sys.db
```

## 6. GitHub Actions での確認方法

### ワークフロー内で確認（デバッグ用）

```yaml
- name: Check DATABASE_URL
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    if [ -z "$DATABASE_URL" ]; then
      echo "⚠️ DATABASE_URL is not set"
    else
      echo "✅ DATABASE_URL is set (length: ${#DATABASE_URL})"
      # セキュリティのため、実際の値は表示しない
    fi
```

## 7. トラブルシューティング

### よくある問題

1. **DATABASE_URL が空の場合**

   - デフォルトの SQLite が使用されます
   - ワークフローでは接続チェックをスキップします

2. **接続エラーの場合**

   - URL の形式を確認: `postgresql://user:password@host:port/dbname`
   - ネットワーク接続を確認
   - 認証情報を確認

3. **環境変数が読み込まれない場合**
   - `.env`ファイルの場所を確認
   - `python-dotenv`がインストールされているか確認
   - 環境変数の設定方法を確認

## 8. セキュリティ注意事項

⚠️ **重要**:

- `DATABASE_URL`には機密情報（パスワードなど）が含まれます
- ログや出力に直接表示しないでください
- GitHub Secrets に適切に保存してください
- 本番環境の URL は絶対に公開しないでください
