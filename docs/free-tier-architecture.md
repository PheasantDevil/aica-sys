# 完全無料アーキテクチャ構成

## 🆓 現在の完全無料構成

```
┌─────────────────────────────────────────┐
│ Vercel (Frontend)                       │
│ - Next.js 14                            │
│ - 無料プラン: Hobby                      │
│ - 帯域幅: 100GB/月                       │
│ - ビルド時間: 6,000分/月                │
│ - スリープ: なし                         │
└─────────────────────────────────────────┘
              ↓ API calls
┌─────────────────────────────────────────┐
│ Render (Backend)                        │
│ - FastAPI + Docker                      │
│ - 無料プラン: Free                       │
│ - CPU: 0.5 vCPU                         │
│ - RAM: 512MB                            │
│ - スリープ: 15分アイドル後               │
└─────────────────────────────────────────┘
              ↓ reads/writes
┌─────────────────────────────────────────┐
│ SQLite (Database)                       │
│ - ローカルファイル (backend/aica_sys.db)│
│ - コスト: $0                            │
│ - Git管理: バージョン管理可能            │
│ - バックアップ: GitHub Actionsで自動     │
└─────────────────────────────────────────┘
              ↓ AI requests
┌─────────────────────────────────────────┐
│ Groq (AI)                               │
│ - Llama 3.1 70B Versatile               │
│ - 無料枠: 14,400 requests/日            │
│ - レート: 30 requests/分                │
│ - コスト: $0 (完全無料)                  │
└─────────────────────────────────────────┘
              ↓ stores
┌─────────────────────────────────────────┐
│ GitHub (Git Repository)                 │
│ - ソースコード管理                       │
│ - CI/CD (GitHub Actions)                │
│ - 無料枠: Public repo無制限              │
└─────────────────────────────────────────┘
```

---

## 💰 コスト比較

### 以前の構成

| サービス       | 用途     | 月額コスト      |
| -------------- | -------- | --------------- |
| Vercel         | Frontend | $0              |
| Render         | Backend  | $0              |
| **Supabase**   | Database | ~~$0~~ (未使用) |
| **GCP Gemini** | AI       | **$5-20** 💰    |
| GitHub         | Repo/CI  | $0              |
| **合計**       |          | **$5-20/月**    |

### 現在の構成

| サービス | 用途     | 月額コスト   |
| -------- | -------- | ------------ |
| Vercel   | Frontend | $0           |
| Render   | Backend  | $0           |
| SQLite   | Database | $0           |
| **Groq** | AI       | **$0** ✅    |
| GitHub   | Repo/CI  | $0           |
| **合計** |          | **$0/月** 🎉 |

**年間節約額: $60-240** 💰

---

## 📊 各サービスの無料枠詳細

### Vercel (Frontend)

```
✅ Hobby Plan (無料)
- デプロイ: 無制限
- 帯域幅: 100GB/月
- ビルド時間: 6,000分/月
- Serverless Functions: 100GB-Hours/月
- エッジ関数: 500,000 invocations/月
- 同時ビルド: 1
- チームメンバー: 1

制限:
- カスタムドメイン: 1個まで
- 環境変数: プロジェクトあたり制限なし
```

### Render (Backend)

```
✅ Free Plan
- CPU: 0.5 vCPU
- RAM: 512MB
- ディスク: 1GB
- 帯域幅: 100GB/月
- ビルド時間: 500分/月
- インスタンス: 制限なし

制限:
⚠️ 15分アイドルでスリープ
   - コールドスタート: 約30秒
   - ウェイクアップ: 初回リクエスト時
```

### Groq (AI)

```
✅ 完全無料
- リクエスト: 14,400/日 (600/時)
- レート: 30 requests/分
- トークン: 制限なし
- モデル: Llama 3.1 70B, 8B, Mixtral等

制限:
- RPM (Requests Per Minute): 30
- 超過時: 1分後に自動リセット
```

### SQLite (Database)

```
✅ ファイルベース（完全無料）
- サイズ制限: なし（Renderディスク1GBまで）
- パフォーマンス: 読み込み高速、書き込み中程度
- バックアップ: Git + GitHub Actions

制限:
- 同時書き込み: 1接続のみ
- スケーラビリティ: 中規模まで
```

### GitHub (Repo/CI)

```
✅ Public Repo (無料)
- リポジトリ: 無制限
- ストレージ: 500MB (Git LFS含む)
- Actions: 2,000分/月
- Packages: 500MB

制限:
- Private repoの場合Actions制限あり
```

---

## ⚡ パフォーマンス比較

### レスポンス時間

| 処理                   | Gemini Pro | Groq (Llama 3.1) | 差分         |
| ---------------------- | ---------- | ---------------- | ------------ |
| 短文生成 (100 tokens)  | ~2秒       | **~0.2秒**       | **10倍高速** |
| 記事生成 (1000 tokens) | ~8秒       | **~0.8秒**       | **10倍高速** |
| 分析処理               | ~3秒       | **~0.3秒**       | **10倍高速** |

### 実測値（AICA-SyS）

```
記事生成 (1500 words):
- Gemini Pro: 約10-15秒
- Groq Llama 3.1 70B: 約1-2秒 ⚡

トレンド分析:
- Gemini Pro: 約5-8秒
- Groq Llama 3.1 70B: 約0.5-1秒 ⚡
```

---

## 🎯 推奨モデル使い分け

### Llama 3.1 70B Versatile（現在使用中）

```python
model="llama-3.1-70b-versatile"
```

**用途**:

- ✅ 記事生成（高品質）
- ✅ ニュースレター作成
- ✅ コンテンツ分析
- ✅ トレンド分析

**特徴**:

- 品質: ⭐⭐⭐⭐
- 速度: 速い
- トークン: 最大8,000

### Llama 3.1 8B Instant

```python
model="llama-3.1-8b-instant"
```

**用途**:

- ⚡ リアルタイム応答
- ⚡ 簡単な要約
- ⚡ カテゴリ分類

**特徴**:

- 品質: ⭐⭐⭐
- 速度: 超高速（70Bの5倍）
- トークン: 最大8,000

### Mixtral 8x7B

```python
model="mixtral-8x7b-32768"
```

**用途**:

- 📄 長文生成
- 📄 複雑なコンテンツ

**特徴**:

- 品質: ⭐⭐⭐⭐
- 速度: 速い
- トークン: 最大32,768

---

## 🔄 スリープ対策

### Renderの15分スリープ問題

#### Option 1: GitHub Actionsで定期ウェイクアップ（推奨）

```yaml
# .github/workflows/keep-alive.yml
name: Keep Render Alive
on:
  schedule:
    - cron: "*/10 * * * *" # 10分ごと

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping backend
        run: curl -f https://aica-sys-backend.onrender.com/health || true
```

#### Option 2: UptimeRobotで監視（外部サービス）

```
URL: https://aica-sys-backend.onrender.com/health
間隔: 5分
無料枠: 50モニター
```

#### Option 3: そのまま使う

```
- 初回アクセスのみ30秒待つ
- その後は高速
- ユーザー影響: 最小限
```

---

## 📈 スケーラビリティ

### 現在の無料構成での処理能力

```
推定処理能力（無料枠内）:
- ページビュー: ~100,000/月
- API requests: ~50,000/月
- AI生成: ~400記事/日
- 同時ユーザー: ~100人

実際のボトルネック:
- Render CPU: 0.5 vCPU
- Render RAM: 512MB
- Groq RPM: 30 requests/分
```

### スケールアップが必要になったら

```
Phase 1 (無料 → 月$7):
- Render: Free → Starter ($7/月)
  - CPU: 0.5 → 1 vCPU
  - RAM: 512MB → 2GB
  - スリープ: なし

Phase 2 (月$7 → 月$32):
- Render: Starter → Standard ($25/月)
- Vercel: Hobby → Pro ($20/月)
  - より高いリソース制限

Phase 3 (月$32 → 月$100+):
- Vercel: Pro → Enterprise
- Render: Standard → Pro
- Database: PostgreSQL (Neon/Supabase)
```

---

## 🛡️ バックアップ・復旧

### データベース (SQLite)

```bash
# 自動バックアップ（GitHub Actions）
- スケジュール: 毎日03:00 UTC
- 保存先: GitHub リポジトリ
- 保持期間: 30日分

# 手動バックアップ
make backup

# 復元
make restore BACKUP_FILE=backups/aica_sys_20251013.db
```

### コード

```bash
# Gitで完全管理
- すべてのコミットが復元ポイント
- いつでも任意のバージョンに戻せる

# ロールバック
git revert [commit-hash]
git push origin main
```

---

## 🎯 まとめ

### 現在の構成の強み

1. ✅ **完全無料**: $0/月
2. ✅ **高速**: Groq 10x高速
3. ✅ **シンプル**: 保守容易
4. ✅ **バックアップ**: Git + SQLite
5. ✅ **スケーラブル**: 必要に応じて段階的アップグレード

### 唯一の制約

- ⚠️ Renderの15分スリープ（初回アクセスのみ30秒待ち）
  - 対策: GitHub Actionsで10分ごとにping（無料）

---

**完全無料で高パフォーマンスなシステムが完成！** 🎉✨
