# データベース移行オプション

## 現状の問題

**Supabaseプロジェクトが一時停止**: AICA-SyS-DBが停止しており、Vercelデプロイが失敗

## 解決策

### オプション1: Supabaseプロジェクトの再開（推奨）

**手順**:
1. [Supabase Dashboard](https://supabase.com/dashboard) にアクセス
2. AICA-SyS-DBプロジェクトを選択
3. "Unpause Project" をクリック
4. 接続情報を確認・更新

**コスト**: 無料枠内（500MB、2GB転送/月）

**メリット**:
- ✅ 既存の設定をそのまま利用
- ✅ PostgreSQL（本番環境推奨）
- ✅ バックアップ・管理機能
- ✅ 設定変更不要

**デメリット**:
- ⚠️ 無料プランは非アクティブで一時停止される
- ⚠️ 定期的な使用が必要

---

### オプション2: Vercel Postgres への移行

**手順**:
1. Vercelダッシュボード → Storage
2. Postgresデータベース作成
3. 環境変数を自動設定
4. マイグレーション実行

**コスト**: 
- Free: $0（256MB、60時間/月）
- Pro: $15/月（256MB、無制限）

**メリット**:
- ✅ Vercel統合（自動設定）
- ✅ 一時停止なし
- ✅ 同じインフラ

**デメリット**:
- ⚠️ 移行作業が必要
- ⚠️ 無料枠が限定的

---

### オプション3: SQLite継続（開発・デモ用）

**手順**:
1. DATABASE_URLを明示的にSQLiteに設定
2. Vercelの環境変数を削除または空にする
3. ファイルベースのSQLite使用

**コスト**: $0

**メリット**:
- ✅ 完全無料
- ✅ 設定不要
- ✅ ローカルと同じ

**デメリット**:
- ❌ 本番環境非推奨
- ❌ スケールしない
- ❌ 同時接続制限

---

### オプション4: Neon Postgres（コスト最適）

**手順**:
1. [Neon](https://neon.tech/) アカウント作成
2. データベース作成
3. 接続文字列を取得
4. Vercel環境変数に設定

**コスト**: 無料枠（512MB、最大10GB転送/月）

**メリット**:
- ✅ 完全無料（Supabaseより寛容）
- ✅ 自動一時停止・再開（スリープ機能）
- ✅ PostgreSQL互換
- ✅ スケーラブル

**デメリット**:
- ⚠️ 移行作業が必要

---

## 推奨案

### 即座の対処: オプション1（Supabase再開）
**理由**: 最も簡単、設定変更不要

### 長期的対策: オプション4（Neon移行）
**理由**: 無料枠が寛容、自動スリープ・再開

---

## Vercelデプロイエラーの早期検出

### CI/CDパイプラインに追加

```yaml
# .github/workflows/backend-ci-cd.yml

- name: Check database connection
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    python3 -c "
    import os
    from sqlalchemy import create_engine
    
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./aica_sys.db')
    
    if 'supabase' in db_url or 'postgres' in db_url:
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute('SELECT 1')
            print('✅ Database connection OK')
        except Exception as e:
            print(f'❌ Database connection failed: {e}')
            print('⚠️  Check if Supabase project is paused')
            exit(1)
    else:
        print('ℹ️  Using SQLite (local only)')
    "
```

### Makefile コマンド追加

```makefile
check-db:
	@echo "Checking database connection..."
	@python3 -c "import os; from backend.database import engine; engine.connect(); print('✅ Database OK')" || echo "❌ Database connection failed"
```

---

## 即座の対処手順

1. **Supabase Dashboard** にアクセス
2. AICA-SyS-DB プロジェクトを **Unpause**
3. Vercelで再デプロイ

または

1. Vercel環境変数から `DATABASE_URL` を削除
2. SQLiteをデフォルト使用（開発用）
3. 後でNeonに移行

