#!/usr/bin/env python3
"""
Supabase設定確認スクリプト
使用方法: python3 scripts/verify_supabase_config.py
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

# .env.localを読み込む
backend_dir = Path(__file__).resolve().parent.parent / "backend"
env_local = backend_dir / ".env.local"
if env_local.exists():
    load_dotenv(env_local)


def check_supabase_config():
    """Supabase設定を確認"""
    print("=" * 60)
    print("Supabase設定確認")
    print("=" * 60)
    
    # 環境変数の確認
    database_url = os.getenv("DATABASE_URL")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
    next_public_supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    next_public_supabase_anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    # DATABASE_URL確認
    print("\n📊 DATABASE_URL:")
    if database_url:
        parsed = urlparse(database_url)
        masked = mask_url(database_url)
        print(f"  ✅ 設定済み: {masked}")
        print(f"  - Host: {parsed.hostname}")
        print(f"  - Port: {parsed.port or 5432}")
        print(f"  - Database: {parsed.path.lstrip('/')}")
        
        # 接続タイプ判定
        if "pooler" in database_url:
            print(f"  - Type: Pooler接続（本番推奨）")
        elif "db." in database_url and ".supabase.co" in database_url:
            print(f"  - Type: Direct接続（開発用）")
        elif "sqlite" in database_url:
            print(f"  - Type: SQLite（ローカル）")
        else:
            print(f"  - Type: その他")
    else:
        print("  ⚠️  未設定")
    
    # SUPABASE_URL確認
    print("\n🌐 SUPABASE_URL:")
    if supabase_url:
        print(f"  ✅ 設定済み: {supabase_url}")
        # Project REF抽出
        if ".supabase.co" in supabase_url:
            project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
            print(f"  - Project REF: {project_ref}")
    else:
        print("  ⚠️  未設定")
    
    # SUPABASE_ANON_KEY確認
    print("\n🔑 SUPABASE_ANON_KEY:")
    if supabase_anon_key:
        print(f"  ✅ 設定済み（長さ: {len(supabase_anon_key)}文字）")
        print(f"  - プレビュー: {supabase_anon_key[:20]}...")
    else:
        print("  ⚠️  未設定")
    
    # SUPABASE_SERVICE_KEY確認
    print("\n🔐 SUPABASE_SERVICE_KEY:")
    if supabase_service_key:
        print(f"  ✅ 設定済み（長さ: {len(supabase_service_key)}文字）")
        print(f"  - プレビュー: {supabase_service_key[:20]}...")
        print(f"  ⚠️  このキーは絶対に公開しないでください！")
    else:
        print("  ⚠️  未設定")
    
    # NEXT_PUBLIC_変数確認
    print("\n🌍 フロントエンド用環境変数:")
    if next_public_supabase_url:
        print(f"  ✅ NEXT_PUBLIC_SUPABASE_URL: {next_public_supabase_url}")
    else:
        print("  ⚠️  NEXT_PUBLIC_SUPABASE_URL: 未設定")
    
    if next_public_supabase_anon_key:
        print(f"  ✅ NEXT_PUBLIC_SUPABASE_ANON_KEY: 設定済み")
    else:
        print("  ⚠️  NEXT_PUBLIC_SUPABASE_ANON_KEY: 未設定")
    
    # 設定の整合性確認
    print("\n" + "=" * 60)
    print("設定整合性チェック")
    print("=" * 60)
    
    issues = []
    
    if database_url and supabase_url:
        # Project REFの一致確認
        db_ref = extract_project_ref(database_url)
        api_ref = extract_project_ref(supabase_url)
        if db_ref and api_ref and db_ref != api_ref:
            issues.append(f"⚠️  DATABASE_URLとSUPABASE_URLのProject REFが一致しません")
    
    if supabase_url and not next_public_supabase_url:
        issues.append("⚠️  SUPABASE_URLは設定されていますが、NEXT_PUBLIC_SUPABASE_URLが未設定です（フロントエンドで使用する場合必要）")
    
    if supabase_anon_key and not next_public_supabase_anon_key:
        issues.append("⚠️  SUPABASE_ANON_KEYは設定されていますが、NEXT_PUBLIC_SUPABASE_ANON_KEYが未設定です（フロントエンドで使用する場合必要）")
    
    if not database_url:
        issues.append("❌ DATABASE_URLが未設定です")
    
    if not supabase_url:
        issues.append("❌ SUPABASE_URLが未設定です")
    
    if issues:
        print("\n発見された問題:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ すべての設定が正しく設定されています！")
    
    return len(issues) == 0

def mask_url(url: str) -> str:
    """URL内のパスワード部分をマスク"""
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        if parsed.password:
            masked = url.replace(f":{parsed.password}@", ":***@")
            return masked
    except:
        pass
    
    return url

def extract_project_ref(url: str) -> str:
    """URLからProject REFを抽出"""
    if not url:
        return None
    
    # supabase.co形式
    if ".supabase.co" in url:
        parts = url.replace("https://", "").replace("http://", "").split(".")
        if len(parts) > 0:
            return parts[0]
    
    # pooler形式
    if "pooler.supabase.com" in url:
        # postgres.[REF]@pooler形式から抽出
        if "postgres." in url:
            start = url.find("postgres.") + 9
            end = url.find("@", start)
            if end > start:
                return url[start:end]
    
    return None

if __name__ == "__main__":
    success = check_supabase_config()
    sys.exit(0 if success else 1)

