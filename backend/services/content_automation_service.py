"""
Content Automation Service for AICA-SyS
Phase 10-1: Automated article generation with Groq API
"""

import logging
import time
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.automated_content import (AutomatedContentDB, ContentStatus,
                                      ContentType, TrendDataDB)
from utils.ai_client import AIClient, ContentGenerationRequest

logger = logging.getLogger(__name__)


class ContentAutomationService:
    """コンテンツ自動生成サービス"""

    def __init__(self, db: Session, groq_api_key: Optional[str] = None):
        self.db = db
        self.ai_client = AIClient(groq_api_key=groq_api_key)

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

    async def generate_article(self, trend: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """記事生成（Groq API使用）"""
        start_time = time.time()

        try:
            # トレンド情報から詳細なトピックを構築
            topic = self._build_topic_description(trend)
            
            # Groq APIで記事生成
            generation_request = ContentGenerationRequest(
                topic=topic,
                content_type="blog_post",
                target_audience="intermediate",
                length="long",
                style="technical"
            )
            
            response = await self.ai_client.generate_content(generation_request)
            
            # 参考リソースを追加
            resources_section = self._generate_resources(trend)
            full_content = f"{response.content}\n\n## 参考リソース\n{resources_section}"
            
            quality_score = self._evaluate_quality(full_content, response)
            generation_time = time.time() - start_time

            # SEOメタデータ生成
            seo_data = {
                'keywords': response.tags,
                'description': response.summary,
                'og_title': response.title,
                'og_description': response.summary
            }

            return {
                'title': response.title,
                'content': full_content,
                'summary': response.summary,
                'tags': response.tags,
                'quality_score': quality_score,
                'generation_time': generation_time,
                'read_time': response.estimated_read_time,
                'seo_data': seo_data,
                'metadata': {
                    'keyword': trend['keyword'],
                    'source_count': trend['source_count'],
                    'trend_score': trend['score'],
                    'ai_model': 'groq-llama-3.3-70b'
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate article for {trend.get('keyword')}: {e}")
            return None

    def _build_topic_description(self, trend: Dict[str, Any]) -> str:
        """トレンド情報から詳細なトピック説明を構築"""
        keyword = trend['keyword']
        source_count = trend['source_count']
        related_items = trend.get('related_items', [])
        
        # 関連記事のタイトルから文脈を抽出
        context_titles = [item.get('title', '') for item in related_items[:3]]
        context = ' | '.join(context_titles) if context_titles else ''
        
        topic = f"{keyword}（TypeScript開発トレンド）"
        if context:
            topic += f" - 文脈: {context}"
        
        topic += f" - {source_count}以上のソースで言及された注目技術"
        return topic

    def _generate_resources(self, trend: Dict[str, Any]) -> str:
        """リソースリンク生成"""
        resources = []
        for item in trend.get('related_items', [])[:5]:
            title = item.get('title', 'リソース')
            url = item.get('source_url', '#')
            source_type = item.get('source_type', 'unknown')
            resources.append(f"- [{title}]({url}) ({source_type})")
        
        if not resources:
            resources.append("- 関連リソースは随時更新されます")
        
        return '\n'.join(resources)

    def _evaluate_quality(self, content: str, ai_response: Any = None) -> float:
        """品質評価（改善版）"""
        score = 60.0
        
        # コンテンツ長
        word_count = len(content.split())
        if word_count > 800:
            score += 15
        elif word_count > 500:
            score += 10
        elif word_count > 300:
            score += 5
        
        # コード例の有無
        if '```' in content:
            score += 10
        
        # 構造化（見出し）
        heading_count = content.count('##')
        if heading_count >= 5:
            score += 10
        elif heading_count >= 3:
            score += 5
        
        # FAQ形式
        if 'FAQ' in content or 'Q:' in content:
            score += 5
        
        # リスト形式
        if content.count('-') >= 5 or content.count('*') >= 5:
            score += 5
        
        # AI応答タグの豊富さ
        if ai_response and hasattr(ai_response, 'tags'):
            if len(ai_response.tags) >= 5:
                score += 5
        
        return min(score, 100.0)

