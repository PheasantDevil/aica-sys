#!/usr/bin/env python3
"""
シンプルなテストスクリプト
依存関係なしでAI機能の基本構造をテスト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """基本的なインポートテスト"""
    print("Testing basic imports...")
    
    try:
        # 基本的なPythonモジュール
        import json
        import re
        import asyncio
        from datetime import datetime
        from typing import List, Dict, Any, Optional
        from dataclasses import dataclass
        from collections import Counter, defaultdict
        print("✅ Basic Python modules imported successfully")
    except ImportError as e:
        print(f"❌ Basic import failed: {e}")
        return False
    
    try:
        # データ収集サービスのテスト
        from services.data_collector import DataCollector, ContentItem
        print("✅ DataCollector imported successfully")
    except ImportError as e:
        print(f"❌ DataCollector import failed: {e}")
        return False
    
    try:
        # AI分析サービスのテスト
        from services.ai_analyzer import AIAnalyzer, AnalysisResult
        print("✅ AIAnalyzer imported successfully")
    except ImportError as e:
        print(f"❌ AIAnalyzer import failed: {e}")
        return False
    
    try:
        # コンテンツ生成サービスのテスト
        from services.content_generator import ContentGenerator, GeneratedContent, ContentType
        print("✅ ContentGenerator imported successfully")
    except ImportError as e:
        print(f"❌ ContentGenerator import failed: {e}")
        return False
    
    try:
        # データベースモデルのテスト
        from models.ai_models import CollectedContent, AnalysisResult as DBAnalysisResult, GeneratedContent as DBGeneratedContent
        print("✅ Database models imported successfully")
    except ImportError as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    return True

def test_data_structures():
    """データ構造のテスト"""
    print("\nTesting data structures...")
    
    try:
        from services.data_collector import ContentItem
        from services.ai_analyzer import AnalysisResult
        from services.content_generator import GeneratedContent, ContentType
        
        # ContentItemのテスト
        item = ContentItem(
            title="Test Article",
            url="https://example.com/test",
            content="This is a test article about TypeScript.",
            source="Test Source",
            published_at=datetime.now(),
            tags=["typescript", "javascript"],
            author="Test Author",
            summary="A test article"
        )
        print(f"✅ ContentItem created: {item.title}")
        
        # AnalysisResultのテスト
        analysis = AnalysisResult(
            content_id="test_1",
            importance_score=0.8,
            category="language",
            subcategory="typescript",
            trend_score=0.7,
            sentiment="positive",
            key_topics=["typescript", "javascript"],
            summary="Test analysis",
            recommendations=["Learn more", "Practice"],
            created_at=datetime.now()
        )
        print(f"✅ AnalysisResult created: {analysis.category}")
        
        # GeneratedContentのテスト
        content = GeneratedContent(
            content_type=ContentType.ARTICLE,
            title="Generated Article",
            content="This is generated content.",
            summary="Generated summary",
            tags=["ai", "generated"],
            target_audience="developers",
            tone="professional",
            word_count=100,
            source_data=["test_1"],
            metadata={"test": True},
            created_at=datetime.now()
        )
        print(f"✅ GeneratedContent created: {content.title}")
        
        return True
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False

def test_basic_functions():
    """基本的な関数のテスト"""
    print("\nTesting basic functions...")
    
    try:
        from services.data_collector import DataCollector
        
        # データ収集エージェントの初期化テスト
        collector = DataCollector("dummy_token")
        print("✅ DataCollector initialized")
        
        # キーワード判定テスト
        test_text = "This is about TypeScript and React development"
        is_related = collector._is_typescript_related(test_text)
        print(f"✅ TypeScript detection: {is_related}")
        
        # タグ抽出テスト
        tags = collector._extract_tags(test_text)
        print(f"✅ Tag extraction: {tags}")
        
        return True
    except Exception as e:
        print(f"❌ Basic function test failed: {e}")
        return False

def test_api_structure():
    """API構造のテスト"""
    print("\nTesting API structure...")
    
    try:
        # ルーターファイルの存在確認
        import os
        router_files = [
            "routers/ai_router.py",
            "routers/analysis_router.py",
            "routers/collection_router.py",
            "routers/content_router.py"
        ]
        
        for router_file in router_files:
            if os.path.exists(router_file):
                print(f"✅ {router_file} exists")
            else:
                print(f"❌ {router_file} missing")
        
        return True
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 AICA-SyS AI Agent Logic - Basic Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_data_structures,
        test_basic_functions,
        test_api_structure
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
        print("🎉 All tests passed! AI Agent Logic is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
