# CLI チートシート

## Vercel CLI

### セットアップ

```bash
npm install -g vercel          # インストール
vercel login                   # ログイン
vercel link                    # プロジェクトリンク
vercel whoami                  # ユーザー確認
```

### デプロイ

```bash
vercel                         # プレビューデプロイ
vercel --prod                  # 本番デプロイ
vercel --force                 # キャッシュ無視
vercel -e NODE_ENV=production  # 環境変数指定
```

### ログ・監視

```bash
vercel logs                    # 最新ログ
vercel logs --follow           # リアルタイムログ
vercel logs [url]              # 特定デプロイのログ
vercel logs --output json      # JSON形式
vercel inspect [url]           # デプロイ詳細
```

### プロジェクト管理

```bash
vercel list                    # デプロイ一覧
vercel projects list           # プロジェクト一覧
vercel env ls                  # 環境変数一覧
vercel env pull                # 環境変数取得
vercel domains ls              # ドメイン一覧
```

### 開発

```bash
vercel dev                     # ローカル開発サーバー
vercel dev --listen 3000       # ポート指定
vercel build                   # ローカルビルド
vercel build --prod            # 本番ビルド
```

---

## Render CLI

### セットアップ

```bash
brew install render            # インストール（macOS）
render login                   # ログイン
render whoami -o json          # ユーザー確認
```

### サービス管理

```bash
render services -o json        # サービス一覧
render deploys -o json         # デプロイ履歴
render restart [service]       # サービス再起動
```

### ログ・監視

```bash
render logs -o json            # ログ取得
render logs --tail             # リアルタイムログ
render logs [service-id]       # 特定サービスのログ
```

### デプロイ

```bash
render deploys [service-id]    # デプロイ一覧
render jobs -o json            # ジョブ一覧
```

### データベース

```bash
render psql [db-id]            # PostgreSQL接続
render pgcli [db-id]           # pgcli接続
render kv-cli [kv-id]          # Redis/Valkey接続
```

### 環境管理

```bash
render environments -o json    # 環境一覧
render projects -o json        # プロジェクト一覧
render workspace               # ワークスペース管理
```

---

## 共通パターン

### 初回セットアップ

```bash
# Vercel
npm install -g vercel
vercel login
cd /path/to/project
vercel link

# Render
brew install render
render login
```

### ログ監視

```bash
# Vercel（リアルタイム）
vercel logs --follow

# Render（リアルタイム）
render logs --tail
```

### デプロイ確認

```bash
# Vercel
vercel list --output json | jq '.[0]'
vercel inspect [url]

# Render
render deploys -o json | jq '.[0]'
```

### トラブルシューティング

```bash
# Vercel
vercel logs [url] --debug
vercel build --debug

# Render
render logs [service-id] -o json
render services -o json | jq '.[] | select(.name=="aica-sys-backend")'
```

---

## Tips

### JSON出力 + jq で便利な使い方

```bash
# Vercel: 最新のデプロイURL取得
vercel list --output json | jq -r '.[0].url'

# Render: サービスステータス確認
render services -o json | jq '.[] | {name: .name, status: .status}'

# Vercel: エラーログのみフィルタ
vercel logs --output json | jq 'select(.level == "error")'
```

### 環境変数の一括管理

```bash
# Vercel: 環境変数をローカルに保存
vercel env pull .env.local

# Vercel: 環境変数を本番に追加
vercel env add DATABASE_URL production

# Vercel: .envファイルから一括インポート
cat .env | while read line; do
  key=$(echo $line | cut -d= -f1)
  val=$(echo $line | cut -d= -f2-)
  vercel env add $key production <<< $val
done
```

### 複数プロジェクトのログ監視

```bash
# tmuxやscreenで複数ペイン使用
tmux new-session \; \
  split-window -h \; \
  send-keys 'cd /path/to/project1 && vercel logs --follow' C-m \; \
  select-pane -t 1 \; \
  send-keys 'render logs --tail' C-m
```

---

## エイリアス設定（お好みで）

```bash
# ~/.zshrc または ~/.bashrc に追加

# Vercel
alias vl='vercel logs --follow'
alias vd='vercel --prod'
alias vdev='vercel dev'
alias vlist='vercel list --output json | jq'

# Render
alias rl='render logs --tail'
alias rs='render services -o json | jq'
alias rd='render deploys -o json | jq'

# 両方
alias deplogs='tmux new-session "vercel logs --follow" \; split-window -h "render logs --tail"'
```
