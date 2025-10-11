"""
Content Automation Service for AICA-SyS
Phase 10-1: Automated article generation
"""

import logging
import time
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from models.automated_content import (AutomatedContentDB, ContentStatus,
                                      ContentType, TrendDataDB)

logger = logging.getLogger(__name__)


class ContentAutomationService:
    """コンテンツ自動生成サービス"""

    def __init__(self, db: Session, openai_api_key: str):
        self.db = db
        self.openai_api_key = openai_api_key

    async def analyze_trends(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """トレンド分析"""
        # キーワード抽出
        keywords = []
        for item in source_data:
            title_words = item.get('title', '').lower().split()
            keywords.extend(title_words)

        # 頻度分析
        keyword_freq = Counter(keywords)
        # 一般的な単語を除外
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keyword_freq = {k: v for k, v in keyword_freq.items() if k not in stopwords and len(k) > 3}

        # トップトレンド抽出
        top_keywords = keyword_freq.most_common(20)

        # トレンドグルーピング
        trends = []
        for keyword, count in top_keywords[:10]:
            related_items = [item for item in source_data if keyword in item.get('title', '').lower()]
            if len(related_items) >= 2:  # 複数ソースで言及
                trends.append({
                    'keyword': keyword,
                    'score': count * len(related_items),
                    'source_count': len(related_items),
                    'related_items': related_items
                })

        # スコアでソート
        trends.sort(key=lambda x: x['score'], reverse=True)
        return trends[:5]

    async def generate_article(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """記事生成"""
        start_time = time.time()

        try:
            # OpenAI API呼び出し（実装は環境に応じて）
            prompt = self._build_prompt(trend)
            article_content = f"""# {trend['keyword'].title()}が注目を集めている理由

## 一言で言うと
{trend['keyword']}は、最近{trend['source_count']}以上の技術コミュニティで注目されている技術トレンドです。

## なぜ今重要なのか
複数の情報源で同時に取り上げられていることから、開発者コミュニティで急速に関心が高まっています。

## 主要な特徴
- 実践的な活用事例が増加
- コミュニティの支持が拡大
- 技術的な成熟度が向上

## 詳細解説
{self._generate_detailed_content(trend)}

## 実装例
```python
# Example implementation
print("Hello, {trend['keyword']}!")
```

## FAQ

**Q: {trend['keyword']}とは何ですか？**
A: {trend['keyword']}は、最新の技術トレンドの一つで、開発者コミュニティで注目されています。

## 参考リソース
{self._generate_resources(trend)}
"""

            quality_score = self._evaluate_quality(article_content)
            generation_time = time.time() - start_time

            return {
                'title': f"{trend['keyword'].title()}が注目を集めている理由",
                'content': article_content,
                'quality_score': quality_score,
                'generation_time': generation_time,
                'metadata': {
                    'keyword': trend['keyword'],
                    'source_count': trend['source_count'],
                    'trend_score': trend['score']
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate article: {e}")
            return None

    def _build_prompt(self, trend: Dict[str, Any]) -> str:
        """プロンプト構築"""
        return f"Write a comprehensive article about {trend['keyword']}"

    def _generate_detailed_content(self, trend: Dict[str, Any]) -> str:
        """詳細コンテンツ生成"""
        return f"詳細な技術解説と実装ガイド（{trend['keyword']}について）"

    def _generate_resources(self, trend: Dict[str, Any]) -> str:
        """リソースリンク生成"""
        resources = []
        for item in trend.get('related_items', [])[:3]:
            resources.append(f"- [{item.get('title')}]({item.get('source_url')})")
        return '\n'.join(resources)

    def _evaluate_quality(self, content: str) -> float:
        """品質評価"""
        score = 70.0
        if len(content) > 1000:
            score += 10
        if '```' in content:
            score += 10
        if '##' in content:
            score += 5
        if 'FAQ' in content:
            score += 5
        return min(score, 100.0)

