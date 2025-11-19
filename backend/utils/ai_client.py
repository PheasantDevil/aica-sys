"""
AI client for AICA-SyS
Handles communication with Groq (Llama 3) and OpenAI
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional

from groq import Groq
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnalysisRequest(BaseModel):
    """Request model for AI analysis"""

    content: str
    content_type: str  # "github_commit", "rss_entry", "web_content", etc.
    context: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for AI analysis"""

    summary: str
    key_points: List[str]
    sentiment: str  # "positive", "neutral", "negative"
    relevance_score: float  # 0.0 to 1.0
    category: str  # "framework", "library", "tool", "language", "ecosystem"
    impact: str  # "low", "medium", "high", "critical"


class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""

    topic: str
    content_type: str  # "blog_post", "newsletter", "social_media"
    target_audience: str  # "beginner", "intermediate", "advanced"
    length: str  # "short", "medium", "long"
    style: str  # "technical", "casual", "formal"


class ContentGenerationResponse(BaseModel):
    """Response model for content generation"""

    title: str
    content: str
    summary: str
    tags: List[str]
    estimated_read_time: int


class AIClient:
    """Client for AI services (Groq and OpenAI)"""

    def __init__(
        self, groq_api_key: Optional[str] = None, openai_api_key: Optional[str] = None
    ):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        # Initialize Groq client
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None

        # OpenAI is kept as fallback (optional)
        self.openai_api_key = openai_api_key

    async def analyze_content(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze content using AI"""
        try:
            # Use Groq (Llama 3.1), fallback to OpenAI if needed
            if self.groq_client:
                return await self._analyze_with_groq(request)
            elif self.openai_api_key:
                return await self._analyze_with_openai(request)
            else:
                raise ValueError("No AI service configured")

        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            # Return default response
            return AnalysisResponse(
                summary="Analysis failed",
                key_points=[],
                sentiment="neutral",
                relevance_score=0.0,
                category="unknown",
                impact="low",
            )

    async def generate_content(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """Generate content using AI"""
        try:
            # Use Groq (Llama 3.1), fallback to OpenAI if needed
            if self.groq_client:
                return await self._generate_with_groq(request)
            elif self.openai_api_key:
                return await self._generate_with_openai(request)
            else:
                raise ValueError("No AI service configured")

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            # Return default response
            return ContentGenerationResponse(
                title="Content Generation Failed",
                content="Unable to generate content at this time.",
                summary="Content generation failed",
                tags=[],
                estimated_read_time=1,
            )

    async def _analyze_with_groq(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze content using Groq (Llama 3.1 70B)"""
        prompt = f"""
        Analyze the following {request.content_type} content for TypeScript ecosystem relevance:
        
        Content: {request.content}
        
        Please provide:
        1. A concise summary (2-3 sentences)
        2. Key points (3-5 bullet points)
        3. Sentiment (positive/neutral/negative)
        4. Relevance score (0.0 to 1.0) for TypeScript developers
        5. Category (framework/library/tool/language/ecosystem)
        6. Impact level (low/medium/high/critical)
        
        Format your response as JSON:
        {{
            "summary": "...",
            "key_points": ["...", "..."],
            "sentiment": "...",
            "relevance_score": 0.0,
            "category": "...",
            "impact": "..."
        }}
        """

        # Groq API call (synchronous, so wrap in asyncio.to_thread)
        def _call_groq():
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # or "llama-3.1-8b-instant" for faster responses
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert TypeScript developer analyzing content for relevance to the TypeScript ecosystem. Always respond with valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return response.choices[0].message.content

        response_text = await asyncio.to_thread(_call_groq)

        # Parse JSON response
        try:
            result = json.loads(response_text)
            return AnalysisResponse(**result)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return self._parse_text_response(response_text)

    async def _generate_with_groq(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """Generate content using Groq (Llama 3.1 70B) with optimized prompts"""
        # Extract SEO keywords from topic
        topic_words = request.topic.lower().split()
        primary_keyword = topic_words[0] if topic_words else "TypeScript"
        secondary_keywords = (
            topic_words[1:6] if len(topic_words) > 1 else ["development", "guide"]
        )

        prompt = f"""
Generate a high-quality {request.content_type} about "{request.topic}" for {request.target_audience} TypeScript developers.

## Content Requirements

### SEO Optimization
- Primary keyword: "{primary_keyword}" (include in title and headings naturally)
- Secondary keywords: {', '.join(secondary_keywords)}
- Title: SEO-optimized, 60 characters or less, include primary keyword
- Meta description: 150-160 characters summary

### Content Quality
- Style: {request.style}
- Length: {request.length}
- Include 2-3 practical code examples with proper syntax highlighting
- Use clear heading hierarchy (H2, H3)
- Add bullet points, numbered lists, and code blocks appropriately
- Include best practices and performance optimization tips
- Address common errors and solutions

### Technical Accuracy
- Reference latest official documentation
- Use current TypeScript/Next.js/React versions
- Provide working, tested code examples
- Follow community best practices

### Engagement
- Start with a hook that addresses reader's pain points
- End with actionable next steps
- Suggest related resources or articles

## Output Format (JSON only)
{{
  "title": "SEO-optimized title with primary keyword",
  "content": "Full article in Markdown format with proper structure",
  "summary": "Meta description (150-160 characters)",
  "tags": ["{primary_keyword}", "{secondary_keywords[0] if secondary_keywords else 'TypeScript'}", ...],
  "estimated_read_time": <number in minutes>
}}

Respond with valid JSON only, no additional text.
"""

        # Groq API call
        def _call_groq():
            system_prompt = """You are an expert TypeScript ecosystem technical writer and content creator.

Your expertise includes:
- TypeScript, JavaScript, Next.js, React, Vue, Node.js and latest technologies
- Official documentation and community best practices
- Practical code examples and performance optimization

Quality standards:
1. Technical accuracy: Follow latest official specs, provide tested code only
2. SEO optimization: Natural keyword placement for both search engines and readers
3. Readability: Clear structure, proper heading hierarchy, visual breaks
4. Practicality: Actionable code examples and best practices readers can implement immediately
5. Engagement: Address reader pain points and provide clear next steps

Always respond with valid JSON format only."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=2048,
            )
            return response.choices[0].message.content

        response_text = await asyncio.to_thread(_call_groq)

        # Parse JSON response
        try:
            result = json.loads(response_text)
            return ContentGenerationResponse(**result)
        except json.JSONDecodeError:
            return self._parse_content_response(response_text)

    async def _analyze_with_openai(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze content using OpenAI (fallback)"""
        # OpenAI implementation kept for fallback
        # Note: Requires openai package and API key
        logger.warning("OpenAI fallback not fully implemented")
        return AnalysisResponse(
            summary="Analysis using fallback",
            key_points=["Fallback analysis"],
            sentiment="neutral",
            relevance_score=0.5,
            category="unknown",
            impact="low",
        )

    async def _generate_with_openai(
        self, request: ContentGenerationRequest
    ) -> ContentGenerationResponse:
        """Generate content using OpenAI (fallback)"""
        # OpenAI implementation kept for fallback
        logger.warning("OpenAI fallback not fully implemented")
        return ContentGenerationResponse(
            title="Generated Content (Fallback)",
            content="Content generation using fallback mode.",
            summary="Fallback content",
            tags=["typescript"],
            estimated_read_time=1,
        )

    def _parse_text_response(self, text: str) -> AnalysisResponse:
        """Parse text response when JSON parsing fails"""
        return AnalysisResponse(
            summary=text[:200] + "..." if len(text) > 200 else text,
            key_points=["Analysis completed"],
            sentiment="neutral",
            relevance_score=0.5,
            category="unknown",
            impact="medium",
        )

    def _parse_content_response(self, text: str) -> ContentGenerationResponse:
        """Parse content response when JSON parsing fails"""
        return ContentGenerationResponse(
            title="Generated Content",
            content=text,
            summary=text[:100] + "..." if len(text) > 100 else text,
            tags=["typescript", "development"],
            estimated_read_time=max(1, len(text.split()) // 200),
        )
