"""
RSS parser for AICA-SyS
"""

import asyncio
import logging
from typing import Dict, List
from urllib.parse import urlparse

import aiohttp
import feedparser

logger = logging.getLogger(__name__)


class RSSParser:
    """Parser for RSS/Atom feeds"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def parse_feed(self, feed_url: str) -> Dict:
        """Parse RSS/Atom feed from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        return {
                            "title": feed.feed.get("title", ""),
                            "description": feed.feed.get("description", ""),
                            "link": feed.feed.get("link", ""),
                            "entries": [
                                {
                                    "title": entry.get("title", ""),
                                    "link": entry.get("link", ""),
                                    "description": entry.get("description", ""),
                                    "summary": entry.get("summary", ""),
                                    "published": entry.get("published", ""),
                                    "tags": [tag.term for tag in entry.get("tags", [])],
                                    "author": entry.get("author", ""),
                                    "content": entry.get("content", [{}])[0].get("value", "") if entry.get("content") else ""
                                }
                                for entry in feed.entries
                            ]
                        }
                    else:
                        logger.error(f"Failed to fetch feed {feed_url}: {response.status}")
                        return {"entries": []}
                        
        except Exception as e:
            logger.error(f"Failed to parse feed {feed_url}: {e}")
            return {"entries": []}
    
    async def parse_multiple_feeds(self, feed_urls: List[str]) -> List[Dict]:
        """Parse multiple RSS feeds concurrently"""
        tasks = [self.parse_feed(url) for url in feed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, dict) and "entries" in result:
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Feed parsing error: {result}")
        
        return valid_results
    
    def is_typescript_related(self, entry: Dict) -> bool:
        """Check if an RSS entry is TypeScript related"""
        typescript_keywords = [
            "typescript", "ts", "type", "types", "typing",
            "react", "nextjs", "vue", "svelte", "angular",
            "node", "deno", "bun", "webpack", "vite",
            "eslint", "prettier", "jest", "cypress"
        ]
        
        text_to_check = " ".join([
            entry.get("title", "").lower(),
            entry.get("description", "").lower(),
            entry.get("summary", "").lower(),
            " ".join(entry.get("tags", [])).lower()
        ])
        
        return any(keyword in text_to_check for keyword in typescript_keywords)
    
    def extract_article_content(self, entry: Dict) -> str:
        """Extract main content from RSS entry"""
        # Try different content fields
        content = (
            entry.get("content", "") or
            entry.get("summary", "") or
            entry.get("description", "")
        )
        
        # Clean up HTML if present
        if content and "<" in content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            content = soup.get_text()
        
        return content.strip()
