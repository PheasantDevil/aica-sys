"""
Content Generation Agent for AICA-SyS
Generates blog posts, newsletters, and social media content
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from models.content import (Article, Newsletter, Trend, TrendCategory,
                            TrendImpact)
from sqlalchemy.orm import Session
from utils.ai_client import (AIClient, ContentGenerationRequest,
                             ContentGenerationResponse)

logger = logging.getLogger(__name__)


class ContentGenerationAgent:
    """Agent responsible for generating content from analyzed data"""
    
    def __init__(self, db: Session, ai_client: AIClient):
        self.db = db
        self.ai_client = ai_client
    
    async def generate_weekly_content(self) -> Dict[str, int]:
        """Generate weekly content including blog posts and newsletter"""
        results = {}
        
        try:
            # Generate blog posts
            blog_count = await self._generate_blog_posts()
            results["blog_posts"] = blog_count
            
            # Generate newsletter
            newsletter_count = await self._generate_newsletter()
            results["newsletter"] = newsletter_count
            
            # Generate social media content
            social_count = await self._generate_social_media_content()
            results["social_media"] = social_count
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
        
        return results
    
    async def _generate_blog_posts(self) -> int:
        """Generate blog posts from analyzed data"""
        logger.info("Generating blog posts...")
        
        # Topics for blog posts based on trends
        topics = [
            "TypeScript 5.0 New Features and Migration Guide",
            "Building Scalable React Apps with TypeScript",
            "Next.js 14 App Router Best Practices",
            "Vue 3 Composition API with TypeScript",
            "Modern JavaScript Tooling: Vite, Bun, and Deno"
        ]
        
        generated_count = 0
        for topic in topics:
            try:
                article = await self._generate_blog_post(topic)
                if article:
                    generated_count += 1
            except Exception as e:
                logger.error(f"Failed to generate blog post for topic '{topic}': {e}")
        
        return generated_count
    
    async def _generate_newsletter(self) -> int:
        """Generate weekly newsletter"""
        logger.info("Generating newsletter...")
        
        try:
            newsletter = await self._create_newsletter()
            if newsletter:
                return 1
        except Exception as e:
            logger.error(f"Failed to generate newsletter: {e}")
        
        return 0
    
    async def _generate_social_media_content(self) -> int:
        """Generate social media content"""
        logger.info("Generating social media content...")
        
        # Generate Twitter/LinkedIn posts
        social_topics = [
            "TypeScript tip of the week",
            "New framework release",
            "Developer tool recommendation",
            "Code snippet showcase"
        ]
        
        generated_count = 0
        for topic in social_topics:
            try:
                content = await self._generate_social_post(topic)
                if content:
                    generated_count += 1
            except Exception as e:
                logger.error(f"Failed to generate social media content for '{topic}': {e}")
        
        return generated_count
    
    async def _generate_blog_post(self, topic: str) -> Optional[Article]:
        """Generate a single blog post"""
        try:
            request = ContentGenerationRequest(
                topic=topic,
                content_type="blog_post",
                target_audience="intermediate",
                length="long",
                style="technical"
            )
            
            response = await self.ai_client.generate_content(request)
            
            # Create article record
            article = Article(
                title=response.title,
                content=response.content,
                summary=response.summary,
                tags=response.tags,
                read_time=response.estimated_read_time,
                is_premium=False,
                author="AICA-SyS"
            )
            
            self.db.add(article)
            self.db.commit()
            
            logger.info(f"Generated blog post: {response.title}")
            return article
            
        except Exception as e:
            logger.error(f"Failed to generate blog post: {e}")
            return None
    
    async def _create_newsletter(self) -> Optional[Newsletter]:
        """Create weekly newsletter"""
        try:
            # Generate newsletter content
            request = ContentGenerationRequest(
                topic="Weekly TypeScript Ecosystem Update",
                content_type="newsletter",
                target_audience="intermediate",
                length="medium",
                style="casual"
            )
            
            response = await self.ai_client.generate_content(request)
            
            # Create newsletter record
            newsletter = Newsletter(
                title=response.title,
                content=response.content,
                subscribers=0,  # Will be updated when subscribers are added
                open_rate=0.0
            )
            
            self.db.add(newsletter)
            self.db.commit()
            
            logger.info(f"Generated newsletter: {response.title}")
            return newsletter
            
        except Exception as e:
            logger.error(f"Failed to generate newsletter: {e}")
            return None
    
    async def _generate_social_post(self, topic: str) -> Optional[Dict]:
        """Generate social media post"""
        try:
            request = ContentGenerationRequest(
                topic=topic,
                content_type="social_media",
                target_audience="intermediate",
                length="short",
                style="casual"
            )
            
            response = await self.ai_client.generate_content(request)
            
            # For now, just log the social media content
            # In a real implementation, this would be posted to social platforms
            logger.info(f"Generated social media post: {response.title}")
            logger.info(f"Content: {response.content}")
            
            return {
                "title": response.title,
                "content": response.content,
                "tags": response.tags
            }
            
        except Exception as e:
            logger.error(f"Failed to generate social media post: {e}")
            return None
    
    async def generate_trend_analysis(self) -> Optional[Trend]:
        """Generate trend analysis from collected data"""
        try:
            # This would analyze recent AnalysisResult records
            # and generate trend insights
            request = ContentGenerationRequest(
                topic="TypeScript Ecosystem Trends Analysis",
                content_type="blog_post",
                target_audience="advanced",
                length="long",
                style="technical"
            )
            
            response = await self.ai_client.generate_content(request)
            
            # Create trend record
            trend = Trend(
                title=response.title,
                description=response.summary,
                category=TrendCategory.ECOSYSTEM,
                impact=TrendImpact.HIGH,
                related_articles=[]
            )
            
            self.db.add(trend)
            self.db.commit()
            
            logger.info(f"Generated trend analysis: {response.title}")
            return trend
            
        except Exception as e:
            logger.error(f"Failed to generate trend analysis: {e}")
            return None
    
    async def get_content_summary(self) -> Dict:
        """Get summary of generated content"""
        try:
            # Query content from database
            total_articles = self.db.query(Article).count()
            recent_articles = self.db.query(Article).filter(
                Article.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()
            
            total_newsletters = self.db.query(Newsletter).count()
            total_trends = self.db.query(Trend).count()
            
            return {
                "total_articles": total_articles,
                "recent_articles": recent_articles,
                "total_newsletters": total_newsletters,
                "total_trends": total_trends,
                "last_generation": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get content summary: {e}")
            return {
                "total_articles": 0,
                "recent_articles": 0,
                "total_newsletters": 0,
                "total_trends": 0,
                "last_generation": None
            }
