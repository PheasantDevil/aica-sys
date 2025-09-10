#!/bin/bash

echo "🔐 AICA-SyS シークレット生成スクリプト"
echo "========================================"

# JWT シークレットキーの生成
echo "📋 JWT シークレットキーを生成中..."
JWT_SECRET=$(openssl rand -base64 32)
echo "JWT_SECRET_KEY=$JWT_SECRET"

# 暗号化キーの生成
echo "📋 暗号化キーを生成中..."
ENCRYPTION_KEY=$(openssl rand -base64 32)
echo "ENCRYPTION_KEY=$ENCRYPTION_KEY"

# NextAuth シークレットの生成
echo "📋 NextAuth シークレットを生成中..."
NEXTAUTH_SECRET=$(openssl rand -base64 32)
echo "NEXTAUTH_SECRET=$NEXTAUTH_SECRET"

echo ""
echo "✅ シークレット生成完了！"
echo ""
echo "これらの値を GitHub Secrets に設定してください："
echo ""
echo "必須の Secrets:"
echo "- JWT_SECRET_KEY: $JWT_SECRET"
echo "- ENCRYPTION_KEY: $ENCRYPTION_KEY"
echo "- NEXTAUTH_SECRET: $NEXTAUTH_SECRET"
echo ""
echo "その他の Secrets は docs/github-secrets-setup.md を参照してください。"
