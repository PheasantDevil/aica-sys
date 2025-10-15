#!/bin/bash

# Docker完全クリーンアップスクリプト
# Homebrew経由でDockerを再インストールするための準備

set -e

echo "🧹 Docker完全クリーンアップ開始..."
echo ""

# 1. Homebrewパッケージのアンインストール
echo "1️⃣ Homebrewパッケージをアンインストール..."
brew uninstall --force docker docker-desktop 2>/dev/null || echo "  ℹ️  Dockerパッケージは既にアンインストール済み"

# 2. Docker Desktop Caskをアンインストール
echo ""
echo "2️⃣ Docker Desktop Caskをアンインストール..."
brew uninstall --cask --force docker 2>/dev/null || echo "  ℹ️  Docker Caskは既にアンインストール済み"

# 3. Dockerプロセスの停止
echo ""
echo "3️⃣ Dockerプロセスを停止..."
pkill -KILL -f Docker 2>/dev/null || echo "  ℹ️  Dockerプロセスは実行されていません"

# 4. ユーザーディレクトリのクリーンアップ
echo ""
echo "4️⃣ ユーザーディレクトリをクリーンアップ..."
rm -rf ~/.docker
echo "  ✅ ~/.docker を削除"

rm -rf ~/Library/Containers/com.docker.docker
echo "  ✅ ~/Library/Containers/com.docker.docker を削除"

rm -rf ~/Library/Application\ Support/Docker\ Desktop
echo "  ✅ ~/Library/Application Support/Docker Desktop を削除"

rm -rf ~/Library/Group\ Containers/group.com.docker
echo "  ✅ ~/Library/Group Containers/group.com.docker を削除"

rm -rf ~/Library/Preferences/com.docker.docker.plist
echo "  ✅ ~/Library/Preferences/com.docker.docker.plist を削除"

rm -rf ~/Library/Saved\ Application\ State/com.electron.docker-frontend.savedState
echo "  ✅ ~/Library/Saved Application State/com.electron.docker-frontend.savedState を削除"

# 5. システムディレクトリのクリーンアップ（sudoが必要）
echo ""
echo "5️⃣ システムディレクトリをクリーンアップ（パスワードが必要です）..."
echo "  ⚠️  管理者パスワードを入力してください"

sudo rm -rf /Library/PrivilegedHelperTools/com.docker.* 2>/dev/null || echo "  ℹ️  システムファイルは既にクリーンアップ済み"
sudo rm -rf /Library/LaunchDaemons/com.docker.* 2>/dev/null || echo "  ℹ️  LaunchDaemonsファイルは既にクリーンアップ済み"
sudo rm -rf /Applications/Docker.app 2>/dev/null || echo "  ℹ️  Docker.appは既に削除済み"

echo "  ✅ システムファイルクリーンアップ完了"

# 6. Homebrewキャッシュのクリーンアップ
echo ""
echo "6️⃣ Homebrewキャッシュをクリーンアップ..."
brew cleanup
echo "  ✅ Homebrewキャッシュクリーンアップ完了"

# 7. 確認
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ クリーンアップ完了！"
echo ""
echo "次のステップ:"
echo "1. Docker Desktopを再インストール:"
echo "   brew install --cask docker"
echo ""
echo "2. Docker Desktopを起動:"
echo "   open -a Docker"
echo ""
echo "3. Docker起動後、動作確認:"
echo "   docker --version"
echo "   docker ps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

