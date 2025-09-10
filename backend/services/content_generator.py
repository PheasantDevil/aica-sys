"""
コンテンツ生成サービス
AIを使用して記事、ニュースレター、ソーシャルメディア投稿を生成
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import openai
import google.generativeai as genai
from PIL import Image
import requests
import json
import re
from dataclasses import dataclass
from enum import Enum

from .data_collector import ContentItem
from .ai_analyzer import AnalysisResult

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """コンテンツタイプ"""
    ARTICLE = "article"
    NEWSLETTER = "newsletter"
    SOCIAL_POST = "social_post"
    BLOG_POST = "blog_post"
    TECHNICAL_GUIDE = "technical_guide"

@dataclass
class GeneratedContent:
    """生成されたコンテンツ"""
    content_type: ContentType
    title: str
    content: str
    summary: str
    tags: List[str]
    target_audience: str
    tone: str
    word_count: int
    created_at: datetime
    source_data: List[str]  # 元データのID
    metadata: Dict[str, Any]

class ContentGenerator:
    """コンテンツ生成サービスのメインクラス"""
    
    def __init__(self, openai_api_key: str, google_ai_api_key: str, stable_diffusion_api_key: str = None):
        # API設定
        openai.api_key = openai_api_key
        genai.configure(api_key=google_ai_api_key)
        self.stable_diffusion_api_key = stable_diffusion_api_key
        
        # モデル初期化
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # コンテンツテンプレート
        self.templates = {
            ContentType.ARTICLE: {
                "structure": "introduction, main_content, conclusion, key_points",
                "tone": "professional, informative, engaging",
                "word_count": 1500
            },
            ContentType.NEWSLETTER: {
                "structure": "header, featured_news, technical_updates, community_highlights, resources",
                "tone": "friendly, informative, community-focused",
                "word_count": 800
            },
            ContentType.SOCIAL_POST: {
                "structure": "hook, main_point, call_to_action",
                "tone": "engaging, conversational, shareable",
                "word_count": 150
            },
            ContentType.BLOG_POST: {
                "structure": "introduction, problem, solution, examples, conclusion",
                "tone": "personal, educational, practical",
                "word_count": 1000
            },
            ContentType.TECHNICAL_GUIDE: {
                "structure": "overview, prerequisites, step_by_step, code_examples, troubleshooting",
                "tone": "technical, clear, detailed",
                "word_count": 2000
            }
        }

    async def generate_content(
        self, 
        content_type: ContentType, 
        analysis_results: List[AnalysisResult],
        target_audience: str = "developers",
        tone: str = "professional"
    ) -> GeneratedContent:
        """コンテンツを生成"""
        logger.info(f"{content_type.value} の生成を開始...")
        
        # 関連する分析結果をフィルタリング
        relevant_results = self._filter_relevant_results(analysis_results, content_type)
        
        if not relevant_results:
            raise ValueError("関連する分析結果が見つかりません")
        
        # プロンプトを生成
        prompt = self._generate_prompt(content_type, relevant_results, target_audience, tone)
        
        # AIでコンテンツを生成
        generated_text = await self._generate_with_ai(prompt, content_type)
        
        # コンテンツを解析・構造化
        structured_content = self._parse_generated_content(generated_text, content_type)
        
        # メタデータを生成
        metadata = self._generate_metadata(relevant_results, content_type)
        
        content = GeneratedContent(
            content_type=content_type,
            title=structured_content["title"],
            content=structured_content["content"],
            summary=structured_content["summary"],
            tags=structured_content["tags"],
            target_audience=target_audience,
            tone=tone,
            word_count=len(structured_content["content"].split()),
            created_at=datetime.now(),
            source_data=[r.content_id for r in relevant_results],
            metadata=metadata
        )
        
        logger.info(f"{content_type.value} の生成完了: {content.word_count} 文字")
        return content

    def _filter_relevant_results(self, results: List[AnalysisResult], content_type: ContentType) -> List[AnalysisResult]:
        """関連する分析結果をフィルタリング"""
        # 重要度とトレンドスコアでソート
        sorted_results = sorted(results, key=lambda x: (x.importance_score + x.trend_score) / 2, reverse=True)
        
        # コンテンツタイプに応じて件数を調整
        limits = {
            ContentType.ARTICLE: 10,
            ContentType.NEWSLETTER: 15,
            ContentType.SOCIAL_POST: 5,
            ContentType.BLOG_POST: 8,
            ContentType.TECHNICAL_GUIDE: 12
        }
        
        return sorted_results[:limits.get(content_type, 10)]

    def _generate_prompt(self, content_type: ContentType, results: List[AnalysisResult], target_audience: str, tone: str) -> str:
        """AI用のプロンプトを生成"""
        template = self.templates[content_type]
        
        # 分析結果から情報を抽出
        topics = []
        summaries = []
        categories = []
        
        for result in results:
            topics.extend(result.key_topics)
            summaries.append(result.summary)
            categories.append(result.category)
        
        # 重複を削除
        topics = list(set(topics))
        categories = list(set(categories))
        
        prompt = f"""
以下の情報を基に、{content_type.value}を生成してください。

【対象読者】: {target_audience}
【トーン】: {tone}
【構造】: {template['structure']}
【推奨文字数】: {template['word_count']}文字

【主要トピック】:
{', '.join(topics[:10])}

【主要カテゴリ】:
{', '.join(categories)}

【参考情報】:
{chr(10).join(summaries[:5])}

【生成要件】:
1. 最新のトレンドを反映した内容
2. 実用的で価値のある情報
3. 読みやすく魅力的な構成
4. 適切な技術用語の使用
5. アクションアイテムや次のステップを含める

【出力形式】:
Title: [タイトル]
Summary: [要約]
Content: [本文]
Tags: [タグ1, タグ2, ...]
"""
        
        return prompt

    async def _generate_with_ai(self, prompt: str, content_type: ContentType) -> str:
        """AIを使用してコンテンツを生成"""
        try:
            # Gemini Proを使用
            response = await self.gemini_model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini Pro生成エラー: {e}")
            
            # フォールバック: OpenAI
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "あなたは技術コンテンツの専門ライターです。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e2:
                logger.error(f"OpenAI生成エラー: {e2}")
                raise Exception("AI生成に失敗しました")

    def _parse_generated_content(self, text: str, content_type: ContentType) -> Dict[str, Any]:
        """生成されたコンテンツを解析・構造化"""
        lines = text.strip().split('\n')
        
        title = ""
        summary = ""
        content = ""
        tags = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
                current_section = "title"
            elif line.startswith("Summary:"):
                summary = line.replace("Summary:", "").strip()
                current_section = "summary"
            elif line.startswith("Content:"):
                content = line.replace("Content:", "").strip()
                current_section = "content"
            elif line.startswith("Tags:"):
                tags_text = line.replace("Tags:", "").strip()
                tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
                current_section = "tags"
            else:
                if current_section == "content":
                    content += "\n" + line
                elif current_section == "summary":
                    summary += " " + line
        
        # デフォルト値の設定
        if not title:
            title = f"TypeScript関連の{content_type.value}"
        if not summary:
            summary = content[:200] + "..." if len(content) > 200 else content
        if not content:
            content = text
        if not tags:
            tags = ["typescript", "javascript", "development"]
        
        return {
            "title": title,
            "summary": summary,
            "content": content,
            "tags": tags
        }

    def _generate_metadata(self, results: List[AnalysisResult], content_type: ContentType) -> Dict[str, Any]:
        """メタデータを生成"""
        return {
            "source_count": len(results),
            "avg_importance_score": sum(r.importance_score for r in results) / len(results),
            "categories": list(set(r.category for r in results)),
            "sentiments": list(set(r.sentiment for r in results)),
            "generation_method": "ai_generated",
            "template_used": content_type.value
        }

    async def generate_image(self, prompt: str, style: str = "technical") -> Optional[str]:
        """画像を生成"""
        if not self.stable_diffusion_api_key:
            logger.warning("Stable Diffusion APIキーが設定されていません")
            return None
        
        try:
            # Stable Diffusion APIを使用（実装は簡略化）
            # 実際の実装では、適切なAPIエンドポイントを使用
            enhanced_prompt = f"{style} style, {prompt}, high quality, professional"
            
            # 画像生成のロジック（実装例）
            logger.info(f"画像生成: {enhanced_prompt}")
            
            # 実際のAPI呼び出しは実装が必要
            return f"generated_image_{hash(prompt)}.png"
            
        except Exception as e:
            logger.error(f"画像生成エラー: {e}")
            return None

    async def generate_newsletter(self, analysis_results: List[AnalysisResult]) -> GeneratedContent:
        """ニュースレターを生成"""
        return await self.generate_content(
            ContentType.NEWSLETTER,
            analysis_results,
            target_audience="TypeScript開発者",
            tone="friendly"
        )

    async def generate_article(self, analysis_results: List[AnalysisResult], topic: str = None) -> GeneratedContent:
        """記事を生成"""
        # 特定のトピックに絞り込む場合
        if topic:
            filtered_results = [r for r in analysis_results if topic.lower() in r.key_topics]
            if not filtered_results:
                filtered_results = analysis_results
        else:
            filtered_results = analysis_results
        
        return await self.generate_content(
            ContentType.ARTICLE,
            filtered_results,
            target_audience="技術者",
            tone="professional"
        )

    async def generate_social_posts(self, analysis_results: List[AnalysisResult], count: int = 3) -> List[GeneratedContent]:
        """ソーシャルメディア投稿を生成"""
        posts = []
        
        # 重要度の高い結果を選択
        high_importance = sorted(analysis_results, key=lambda x: x.importance_score, reverse=True)[:count]
        
        for result in high_importance:
            post = await self.generate_content(
                ContentType.SOCIAL_POST,
                [result],
                target_audience="開発者コミュニティ",
                tone="engaging"
            )
            posts.append(post)
        
        return posts

    async def generate_technical_guide(self, analysis_results: List[AnalysisResult], topic: str) -> GeneratedContent:
        """技術ガイドを生成"""
        # 特定のトピックに関連する結果をフィルタリング
        relevant_results = [r for r in analysis_results if topic.lower() in r.key_topics or topic.lower() in r.category]
        
        if not relevant_results:
            relevant_results = analysis_results
        
        return await self.generate_content(
            ContentType.TECHNICAL_GUIDE,
            relevant_results,
            target_audience="中級〜上級開発者",
            tone="technical"
        )

# 使用例
async def main():
    """コンテンツ生成の実行例"""
    openai_api_key = "your_openai_api_key"
    google_ai_api_key = "your_google_ai_api_key"
    
    generator = ContentGenerator(openai_api_key, google_ai_api_key)
    
    # サンプル分析結果
    sample_results = [
        AnalysisResult(
            content_id="test_1",
            importance_score=0.8,
            category="framework",
            subcategory="react",
            trend_score=0.7,
            sentiment="positive",
            key_topics=["react", "typescript", "hooks"],
            summary="React 18の新機能について",
            recommendations=["最新版にアップデート", "新機能を試す"],
            created_at=datetime.now()
        )
    ]
    
    # 記事を生成
    article = await generator.generate_article(sample_results)
    print(f"生成された記事: {article.title}")
    
    # ニュースレターを生成
    newsletter = await generator.generate_newsletter(sample_results)
    print(f"生成されたニュースレター: {newsletter.title}")

if __name__ == "__main__":
    asyncio.run(main())
