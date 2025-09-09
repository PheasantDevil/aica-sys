"""
AI client for AICA-SyS
Handles communication with Google AI Studio (Gemini) and OpenAI
"""

import asyncio
import logging
from typing import Dict, List, Optional

import google.generativeai as genai
import openai
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
    """Client for AI services (Gemini and OpenAI)"""
    
    def __init__(self, google_api_key: Optional[str] = None, openai_api_key: Optional[str] = None):
        self.google_api_key = google_api_key
        self.openai_api_key = openai_api_key
        
        # Initialize Google AI
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
        
        # Initialize OpenAI
        if openai_api_key:
            openai.api_key = openai_api_key
        else:
            openai.api_key = None
    
    async def analyze_content(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze content using AI"""
        try:
            # Try Gemini first, fallback to OpenAI
            if self.gemini_model:
                return await self._analyze_with_gemini(request)
            elif openai.api_key:
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
                impact="low"
            )
    
    async def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate content using AI"""
        try:
            # Try Gemini first, fallback to OpenAI
            if self.gemini_model:
                return await self._generate_with_gemini(request)
            elif openai.api_key:
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
                estimated_read_time=1
            )
    
    async def _analyze_with_gemini(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze content using Gemini"""
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
        
        response = await asyncio.to_thread(
            self.gemini_model.generate_content, prompt
        )
        
        # Parse JSON response
        import json
        try:
            result = json.loads(response.text)
            return AnalysisResponse(**result)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            return self._parse_gemini_text_response(response.text)
    
    async def _analyze_with_openai(self, request: AnalysisRequest) -> AnalysisResponse:
        """Analyze content using OpenAI"""
        prompt = f"""
        Analyze the following {request.content_type} content for TypeScript ecosystem relevance:
        
        Content: {request.content}
        
        Provide a JSON response with:
        - summary: concise summary (2-3 sentences)
        - key_points: array of 3-5 key points
        - sentiment: positive/neutral/negative
        - relevance_score: number between 0.0 and 1.0
        - category: framework/library/tool/language/ecosystem
        - impact: low/medium/high/critical
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert TypeScript developer analyzing content for relevance to the TypeScript ecosystem."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            return AnalysisResponse(**result)
        except json.JSONDecodeError:
            return self._parse_openai_text_response(response.choices[0].message.content)
    
    async def _generate_with_gemini(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate content using Gemini"""
        prompt = f"""
        Generate a {request.content_type} about {request.topic} for {request.target_audience} TypeScript developers.
        
        Requirements:
        - Style: {request.style}
        - Length: {request.length}
        - Include practical examples and code snippets
        - Make it engaging and informative
        
        Provide a JSON response with:
        - title: compelling title
        - content: full article content
        - summary: 2-3 sentence summary
        - tags: array of relevant tags
        - estimated_read_time: estimated reading time in minutes
        """
        
        response = await asyncio.to_thread(
            self.gemini_model.generate_content, prompt
        )
        
        import json
        try:
            result = json.loads(response.text)
            return ContentGenerationResponse(**result)
        except json.JSONDecodeError:
            return self._parse_gemini_content_response(response.text)
    
    async def _generate_with_openai(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate content using OpenAI"""
        prompt = f"""
        Generate a {request.content_type} about {request.topic} for {request.target_audience} TypeScript developers.
        
        Style: {request.style}
        Length: {request.length}
        
        Include practical examples and code snippets. Make it engaging and informative.
        
        Provide JSON response with title, content, summary, tags, and estimated_read_time.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert TypeScript developer and technical writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            return ContentGenerationResponse(**result)
        except json.JSONDecodeError:
            return self._parse_openai_content_response(response.choices[0].message.content)
    
    def _parse_gemini_text_response(self, text: str) -> AnalysisResponse:
        """Parse Gemini text response when JSON parsing fails"""
        return AnalysisResponse(
            summary=text[:200] + "..." if len(text) > 200 else text,
            key_points=["Analysis completed"],
            sentiment="neutral",
            relevance_score=0.5,
            category="unknown",
            impact="medium"
        )
    
    def _parse_openai_text_response(self, text: str) -> AnalysisResponse:
        """Parse OpenAI text response when JSON parsing fails"""
        return AnalysisResponse(
            summary=text[:200] + "..." if len(text) > 200 else text,
            key_points=["Analysis completed"],
            sentiment="neutral",
            relevance_score=0.5,
            category="unknown",
            impact="medium"
        )
    
    def _parse_gemini_content_response(self, text: str) -> ContentGenerationResponse:
        """Parse Gemini content response when JSON parsing fails"""
        return ContentGenerationResponse(
            title="Generated Content",
            content=text,
            summary=text[:100] + "..." if len(text) > 100 else text,
            tags=["typescript", "development"],
            estimated_read_time=5
        )
    
    def _parse_openai_content_response(self, text: str) -> ContentGenerationResponse:
        """Parse OpenAI content response when JSON parsing fails"""
        return ContentGenerationResponse(
            title="Generated Content",
            content=text,
            summary=text[:100] + "..." if len(text) > 100 else text,
            tags=["typescript", "development"],
            estimated_read_time=5
        )
