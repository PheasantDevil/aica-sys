# Docker セットアップガイド

## 概要

AICA-SySでSupabase CLIのローカル開発環境を使用するため、Docker Desktopをセットアップします。

## 問題: Docker再インストールエラー

### 症状

```
Error: docker-desktop: Failure while executing; `/usr/bin/sudo ...` exited with 1.
sudo: a terminal is required to read the password
```

### 原因

- Docker Desktop の残ファイルが存在
- 特権ヘルパーツール（PrivilegedHelperTools）が削除できていない
- sudoパスワードが必要だが対話的に入力できない

## 解決方法

### 方法1: 自動クリーンアップスクリプト使用（推奨）

```bash
# クリーンアップスクリプトを実行（パスワード入力が必要）
./scripts/cleanup-docker.sh

# スクリプトが完了したら、Dockerを再インストール
brew install --cask docker

# Docker Desktopを起動
open -a Docker

# 動作確認
docker --version
docker ps
```

### 方法2: 手動クリーンアップ

#### ステップ1: Homebrewパッケージ削除

```bash
# Docker関連パッケージをアンインストール
brew uninstall --force docker docker-desktop
brew uninstall --cask --force docker
```

#### ステップ2: ユーザーディレクトリクリーンアップ

```bash
rm -rf ~/.docker
rm -rf ~/Library/Containers/com.docker.docker
rm -rf ~/Library/Application\ Support/Docker\ Desktop
rm -rf ~/Library/Group\ Containers/group.com.docker
rm -rf ~/Library/Preferences/com.docker.docker.plist
rm -rf ~/Library/Saved\ Application\ State/com.electron.docker-frontend.savedState
```

#### ステップ3: システムディレクトリクリーンアップ（sudoが必要）

**ターミナルで以下を手動実行：**

```bash
sudo rm -rf /Library/PrivilegedHelperTools/com.docker.*
sudo rm -rf /Library/LaunchDaemons/com.docker.*
sudo rm -rf /Applications/Docker.app
```

#### ステップ4: 再インストール

```bash
# Homebrewキャッシュをクリア
brew cleanup

# Docker Desktopをインストール
brew install --cask docker

# Docker Desktopを起動
open -a Docker
```

#### ステップ5: 初回セットアップ

1. Docker Desktopが起動したら、利用規約に同意
2. 「Use recommended settings」を選択
3. 設定完了を待つ（数分かかる場合あります）

#### ステップ6: 動作確認

```bash
# Dockerバージョン確認
docker --version

# Docker動作確認
docker ps

# Docker Composeバージョン確認
docker compose version
```

### 方法3: 公式インストーラー使用

Homebrewで問題が解決しない場合：

1. [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)から直接ダウンロード
2. DMGファイルをマウント
3. Docker.appを/Applicationsにドラッグ
4. Docker Desktopを起動

## Docker Desktop 設定

### 推奨設定

#### Resources（リソース）

- **CPU**: 4コア（最小2コア）
- **Memory**: 4GB（最小2GB）
- **Swap**: 1GB
- **Disk image size**: 60GB

#### General（一般）

- [x] Start Docker Desktop when you log in
- [x] Use Docker Compose V2

#### Advanced（詳細）

- [x] Enable VirtioFS accelerated directory sharing（macOSのみ）

## Supabase ローカル開発環境

### Docker起動後、Supabaseローカル環境を起動

```bash
cd /Users/Work/aica-sys

# Supabaseローカル環境を起動
supabase start

# 起動後の情報が表示されます:
# API URL: http://localhost:54321
# GraphiQL: http://localhost:54323/graphql/v1
# DB URL: postgresql://postgres:postgres@localhost:54322/postgres
# Studio URL: http://localhost:54323
# Inbucket URL: http://localhost:54324
# JWT secret: super-secret-jwt-token-with-at-least-32-characters-long
# anon key: eyJhbGc...
# service_role key: eyJhbGc...
```

### Supabaseローカル環境の停止

```bash
# Supabaseコンテナを停止
supabase stop

# すべてのデータを削除して停止
supabase stop --no-backup
```

### Supabaseローカル環境のリセット

```bash
# データベースをリセット
supabase db reset

# マイグレーションを再適用
supabase db push
```

## トラブルシューティング

### エラー: "Cannot connect to the Docker daemon"

**原因**: Docker Desktopが起動していない

**解決**:

```bash
# Docker Desktopを起動
open -a Docker

# 起動完了を待つ（メニューバーにアイコンが表示される）
sleep 30

# 動作確認
docker ps
```

### エラー: "port is already allocated"

**原因**: ポートが他のサービスで使用中

**解決**:

```bash
# 使用中のポートを確認
lsof -i :54321
lsof -i :54322
lsof -i :54323

# プロセスを停止
kill -9 <PID>

# または、Supabaseのポートを変更
# supabase/config.toml を編集
```

### エラー: "Docker Desktop requires macOS 10.15 or later"

**原因**: macOSバージョンが古い

**解決**:

1. macOSをアップデート
2. または、古いバージョンのDocker Desktopをインストール

### Homebrewで "zsh: command not found: brew"

**原因**: Homebrewがインストールされていない、またはPATHが設定されていない

**解決**:

```bash
# Homebrewインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# PATHに追加（Apple Silicon）
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"

# PATHに追加（Intel Mac）
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

## 代替案: Docker使用せずにSupabase連携

Docker Desktop不要で、リモートSupabaseのみ使用する方法：

### 1. リモートSupabaseのみ使用

```bash
# ローカル環境不要、リモートDBに直接接続
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres

# マイグレーションはリモートに直接適用
supabase db push
```

### 2. psqlで直接操作

```bash
# PostgreSQLクライアントのみインストール
brew install postgresql

# リモートDBに接続
psql "postgresql://postgres:[PASSWORD]@db.ndetbklyymekcifheqaj.supabase.co:5432/postgres"

# SQLファイルを実行
psql "postgresql://..." < backend/security/enable_rls.sql
```

### 3. Supabase Dashboardで管理

- すべての操作をWeb UIで実行
- SQL Editorでクエリ実行
- マイグレーションは手動コピー＆実行

## Docker Desktop インストール後の確認

### 必須確認項目

```bash
# 1. Dockerバージョン確認
docker --version
# Docker version 27.x.x以上

# 2. Docker Compose確認
docker compose version
# Docker Compose version v2.x.x以上

# 3. Docker動作確認
docker run hello-world

# 4. Supabase起動テスト
cd /Users/Work/aica-sys
supabase start
```

## AICA-SySプロジェクトでの使用

### Docker使用ケース

1. **Supabaseローカル開発環境**

   ```bash
   supabase start
   # ローカルでDBテスト、マイグレーション検証
   ```

2. **コンテナ化されたバックエンド**

   ```bash
   docker compose up -d
   # backend, PostgreSQL, Redis, Qdrantを起動
   ```

3. **統合テスト**
   ```bash
   docker compose -f docker-compose.test.yml up
   ```

### Docker不使用ケース

1. **本番環境**
   - Vercel（フロントエンド）
   - Render（バックエンド）
   - Supabase（データベース）

2. **シンプルな開発**
   - SQLite（ローカルDB）
   - uvicorn（バックエンド）
   - next dev（フロントエンド）

## まとめ

### Docker必要な場合

- ✅ Supabaseローカル環境使用
- ✅ 完全な統合テスト実行
- ✅ コンテナ化検証

### Docker不要な場合

- ✅ リモートSupabaseのみ使用
- ✅ SQLiteでローカル開発
- ✅ シンプルな開発・テスト

**推奨**: 本番環境に近いテストが必要な場合はDocker使用、シンプルな開発ならDocker不要

## 参考リンク

- [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Homebrew Docker](https://formulae.brew.sh/cask/docker)
- [Supabase CLI + Docker](https://supabase.com/docs/guides/cli/local-development)
