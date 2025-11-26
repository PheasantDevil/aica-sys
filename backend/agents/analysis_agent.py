"""
Analysis Agent for AICA-SyS
Analyzes collected information using AI
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models.collection import AnalysisResult, Sentiment
from utils.ai_client import AIClient, AnalysisRequest

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent responsible for analyzing collected information"""

    def __init__(self, db: Session, ai_client: AIClient):
        self.db = db
        self.ai_client = ai_client

    async def analyze_collected_data(self) -> Dict[str, int]:
        """Analyze all collected data"""
        results = {}

        try:
            # Analyze GitHub data
            github_count = await self._analyze_github_data()
            results["github"] = github_count

            # Analyze RSS data
            rss_count = await self._analyze_rss_data()
            results["rss"] = rss_count

            # Analyze web scraping data
            web_count = await self._analyze_web_data()
            results["web"] = web_count

            # Generate trend analysis
            await self._generate_trend_analysis()

        except Exception as e:
            logger.error(f"Analysis failed: {e}")

        return results

    async def _analyze_github_data(self) -> int:
        """Analyze GitHub collected data"""
        # This would typically query raw GitHub data from database
        # For now, we'll simulate the analysis
        logger.info("Analyzing GitHub data...")

        # Simulate analyzing GitHub commits, issues, and releases
        sample_github_data = [
            {
                "content": "TypeScript 5.0 introduces new decorator syntax and improved performance",
                "content_type": "github_release",
                "source_id": "typescript-5.0-release",
            },
            {
                "content": "Next.js 14 adds App Router improvements and better TypeScript support",
                "content_type": "github_commit",
                "source_id": "nextjs-14-commit",
            },
        ]

        analyzed_count = 0
        for data in sample_github_data:
            try:
                analysis = await self._analyze_single_item(data)
                if analysis:
                    analyzed_count += 1
            except Exception as e:
                logger.error(f"Failed to analyze GitHub item: {e}")

        return analyzed_count

    async def _analyze_rss_data(self) -> int:
        """Analyze RSS collected data"""
        logger.info("Analyzing RSS data...")

        # Simulate analyzing RSS entries
        sample_rss_data = [
            {
                "content": "New TypeScript features in React 18: better type inference and performance",
                "content_type": "rss_entry",
                "source_id": "react-18-typescript",
            },
            {
                "content": "Vue 3 with TypeScript: composition API and better developer experience",
                "content_type": "rss_entry",
                "source_id": "vue3-typescript",
            },
        ]

        analyzed_count = 0
        for data in sample_rss_data:
            try:
                analysis = await self._analyze_single_item(data)
                if analysis:
                    analyzed_count += 1
            except Exception as e:
                logger.error(f"Failed to analyze RSS item: {e}")

        return analyzed_count

    async def _analyze_web_data(self) -> int:
        """Analyze web scraped data"""
        logger.info("Analyzing web scraped data...")

        # Simulate analyzing web content
        sample_web_data = [
            {
                "content": "TypeScript 5.0 migration guide: new features and breaking changes",
                "content_type": "web_content",
                "source_id": "typescript-migration-guide",
            },
            {
                "content": "Building scalable React apps with TypeScript and modern tooling",
                "content_type": "web_content",
                "source_id": "react-typescript-scalable",
            },
        ]

        analyzed_count = 0
        for data in sample_web_data:
            try:
                analysis = await self._analyze_single_item(data)
                if analysis:
                    analyzed_count += 1
            except Exception as e:
                logger.error(f"Failed to analyze web item: {e}")

        return analyzed_count

    async def _analyze_single_item(self, data: Dict) -> Optional[AnalysisResult]:
        """Analyze a single item using AI"""
        try:
            request = AnalysisRequest(
                content=data["content"],
                content_type=data["content_type"],
                context="TypeScript ecosystem analysis",
            )

            analysis = await self.ai_client.analyze_content(request)

            # Create analysis result record
            result = AnalysisResult(
                source_id=data["source_id"],
                title=(
                    data["content"][:100] + "..."
                    if len(data["content"]) > 100
                    else data["content"]
                ),
                summary=analysis.summary,
                key_points=analysis.key_points,
                sentiment=Sentiment(analysis.sentiment),
                relevance=analysis.relevance_score,
            )

            self.db.add(result)
            self.db.commit()

            logger.info(f"Analyzed item: {data['source_id']}")
            return result

        except Exception as e:
            logger.error(
                f"Failed to analyze item {data.get('source_id', 'unknown')}: {e}"
            )
            return None

    async def _generate_trend_analysis(self) -> None:
        """Generate trend analysis from analyzed data"""
        logger.info("Generating trend analysis...")

        # This would typically analyze all AnalysisResult records
        # and generate trend insights
        try:
            # Simulate trend analysis
            trends = [
                {
                    "title": "TypeScript 5.0 Adoption",
                    "description": "Growing adoption of TypeScript 5.0 with new decorator syntax",
                    "category": "language",
                    "impact": "high",
                },
                {
                    "title": "Next.js App Router",
                    "description": "Increased usage of Next.js App Router with TypeScript",
                    "category": "framework",
                    "impact": "medium",
                },
            ]

            for trend in trends:
                logger.info(f"Trend identified: {trend['title']}")

        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")

    async def get_analysis_summary(self) -> Dict:
        """Get summary of analysis results"""
        try:
            # Query analysis results from database
            total_analyzed = self.db.query(AnalysisResult).count()
            recent_analyzed = (
                self.db.query(AnalysisResult)
                .filter(
                    AnalysisResult.created_at
                    >= datetime.utcnow().replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                )
                .count()
            )

            # Get sentiment distribution
            positive_count = (
                self.db.query(AnalysisResult)
                .filter(AnalysisResult.sentiment == Sentiment.POSITIVE)
                .count()
            )
            neutral_count = (
                self.db.query(AnalysisResult)
                .filter(AnalysisResult.sentiment == Sentiment.NEUTRAL)
                .count()
            )
            negative_count = (
                self.db.query(AnalysisResult)
                .filter(AnalysisResult.sentiment == Sentiment.NEGATIVE)
                .count()
            )

            return {
                "total_analyzed": total_analyzed,
                "recent_analyzed": recent_analyzed,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "neutral": neutral_count,
                    "negative": negative_count,
                },
                "last_analysis": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get analysis summary: {e}")
            return {
                "total_analyzed": 0,
                "recent_analyzed": 0,
                "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "last_analysis": None,
            }
