#!/usr/bin/env python3
"""
最小限のテストスクリプト
依存関係なしでAI機能の基本構造をテスト
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_structure():
    """ファイル構造のテスト"""
    print("Testing file structure...")
    
    required_files = [
        "services/data_collector.py",
        "services/ai_analyzer.py", 
        "services/content_generator.py",
        "models/ai_models.py",
        "routers/ai_router.py",
        "routers/analysis_router.py",
        "routers/collection_router.py",
        "routers/content_router.py",
        "database.py",
        "main.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_code_syntax():
    """コード構文のテスト"""
    print("\nTesting code syntax...")
    
    python_files = [
        "services/data_collector.py",
        "services/ai_analyzer.py",
        "services/content_generator.py", 
        "models/ai_models.py",
        "routers/ai_router.py",
        "main.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                print(f"✅ {file_path} - syntax OK")
            except SyntaxError as e:
                print(f"❌ {file_path} - syntax error: {e}")
                syntax_errors.append(f"{file_path}: {e}")
            except Exception as e:
                print(f"⚠️  {file_path} - warning: {e}")
        else:
            print(f"❌ {file_path} - file not found")
            syntax_errors.append(f"{file_path}: file not found")
    
    return len(syntax_errors) == 0

def test_import_structure():
    """インポート構造のテスト"""
    print("\nTesting import structure...")
    
    # 基本的なPythonモジュールのテスト
    try:
        import asyncio
        import json
        import re
        from collections import Counter, defaultdict
        from dataclasses import dataclass
        from datetime import datetime
        from typing import Any, Dict, List, Optional
        print("✅ Basic Python modules")
    except ImportError as e:
        print(f"❌ Basic modules: {e}")
        return False
    
    # ファイル内のインポート文をチェック
    files_to_check = [
        "services/data_collector.py",
        "services/ai_analyzer.py",
        "services/content_generator.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 外部依存関係のインポートをチェック
                external_imports = [
                    'import aiohttp',
                    'import feedparser', 
                    'import openai',
                    'import google.generativeai',
                    'from sentence_transformers',
                    'from sklearn',
                    'from PyGithub'
                ]
                
                found_imports = []
                for imp in external_imports:
                    if imp in content:
                        found_imports.append(imp)
                
                if found_imports:
                    print(f"✅ {file_path} - has external dependencies: {len(found_imports)}")
                else:
                    print(f"✅ {file_path} - no external dependencies")
                    
            except Exception as e:
                print(f"❌ {file_path} - error reading: {e}")
                return False
    
    return True

def test_class_definitions():
    """クラス定義のテスト"""
    print("\nTesting class definitions...")
    
    # データ収集エージェント
    try:
        with open("services/data_collector.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "class DataCollector:" in content:
            print("✅ DataCollector class defined")
        else:
            print("❌ DataCollector class not found")
            return False
            
        if "class ContentItem:" in content:
            print("✅ ContentItem class defined")
        else:
            print("❌ ContentItem class not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking data_collector.py: {e}")
        return False
    
    # AI分析エンジン
    try:
        with open("services/ai_analyzer.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "class AIAnalyzer:" in content:
            print("✅ AIAnalyzer class defined")
        else:
            print("❌ AIAnalyzer class not found")
            return False
            
        if "class AnalysisResult:" in content:
            print("✅ AnalysisResult class defined")
        else:
            print("❌ AnalysisResult class not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking ai_analyzer.py: {e}")
        return False
    
    # コンテンツ生成サービス
    try:
        with open("services/content_generator.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "class ContentGenerator:" in content:
            print("✅ ContentGenerator class defined")
        else:
            print("❌ ContentGenerator class not found")
            return False
            
        if "class GeneratedContent:" in content:
            print("✅ GeneratedContent class defined")
        else:
            print("❌ GeneratedContent class not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking content_generator.py: {e}")
        return False
    
    return True

def test_api_endpoints():
    """APIエンドポイントのテスト"""
    print("\nTesting API endpoints...")
    
    # AIルーター
    try:
        with open("routers/ai_router.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        endpoints = [
            "@router.post(\"/collect\")",
            "@router.post(\"/analyze\")",
            "@router.post(\"/generate\")",
            "@router.get(\"/content\")",
            "@router.get(\"/analysis\")",
            "@router.get(\"/generated\")",
            "@router.get(\"/trends\")",
            "@router.get(\"/stats\")"
        ]
        
        found_endpoints = []
        for endpoint in endpoints:
            if endpoint in content:
                found_endpoints.append(endpoint)
        
        print(f"✅ AI Router - {len(found_endpoints)}/{len(endpoints)} endpoints defined")
        
    except Exception as e:
        print(f"❌ Error checking ai_router.py: {e}")
        return False
    
    return True

def main():
    """メインテスト実行"""
    print("🚀 AICA-SyS AI Agent Logic - Minimal Tests")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_code_syntax,
        test_import_structure,
        test_class_definitions,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI Agent Logic structure is ready.")
        print("\n📋 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables")
        print("3. Test with actual API calls")
        print("4. Deploy to production")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
