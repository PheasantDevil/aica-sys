"""
Web scraper for AICA-SyS
"""

import asyncio
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    """Web scraper for collecting content from websites"""

    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_url(self, url: str) -> Optional[Dict]:
        """Scrape content from a single URL"""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        return await self._parse_html(html, url)
                    else:
                        logger.error(f"Failed to fetch {url}: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return None

    async def scrape_multiple_urls(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs concurrently"""
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None results and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping error: {result}")

        return valid_results

    async def _parse_html(self, html: str, url: str) -> Dict:
        """Parse HTML content and extract relevant information"""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Extract title
        title = ""
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text().strip()

        # Extract meta description
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "").strip()

        # Extract main content
        content = ""

        # Try to find main content area
        main_content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
            or soup.find("div", class_="post-content")
            or soup.find("div", class_="entry-content")
        )

        if main_content:
            content = main_content.get_text(separator=" ", strip=True)
        else:
            # Fallback to body content
            body = soup.find("body")
            if body:
                content = body.get_text(separator=" ", strip=True)

        # Extract links
        links = []
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if href:
                full_url = urljoin(url, href)
                link_text = link.get_text().strip()
                if link_text and len(link_text) < 100:  # Reasonable link text length
                    links.append({"url": full_url, "text": link_text})

        # Extract images
        images = []
        for img in soup.find_all("img", src=True):
            src = img.get("src")
            if src:
                full_url = urljoin(url, src)
                alt_text = img.get("alt", "")
                images.append({"url": full_url, "alt": alt_text})

        return {
            "url": url,
            "title": title,
            "description": description,
            "content": content,
            "links": links[:20],  # Limit to 20 links
            "images": images[:10],  # Limit to 10 images
            "word_count": len(content.split()),
            "is_typescript_related": self._is_typescript_related(
                title + " " + description + " " + content
            ),
        }

    def _is_typescript_related(self, text: str) -> bool:
        """Check if content is TypeScript related"""
        typescript_keywords = [
            "typescript",
            "ts",
            "type",
            "types",
            "typing",
            "react",
            "nextjs",
            "vue",
            "svelte",
            "angular",
            "node",
            "deno",
            "bun",
            "webpack",
            "vite",
            "eslint",
            "prettier",
            "jest",
            "cypress",
            "javascript",
            "js",
            "ecmascript",
            "es6",
            "es2015",
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in typescript_keywords)

    async def scrape_blog_posts(self, base_url: str, max_pages: int = 5) -> List[Dict]:
        """Scrape blog posts from a website"""
        posts = []

        try:
            # First, get the main page to find blog post links
            main_content = await self.scrape_url(base_url)
            if not main_content:
                return posts

            # Find blog post links
            blog_links = []
            for link in main_content.get("links", []):
                link_text = link.get("text", "").lower()
                link_url = link.get("url", "")

                # Look for blog post indicators
                if any(
                    indicator in link_text
                    for indicator in ["blog", "post", "article", "news"]
                ):
                    blog_links.append(link_url)

            # Scrape each blog post
            for link_url in blog_links[:max_pages]:
                post_content = await self.scrape_url(link_url)
                if post_content and post_content.get("is_typescript_related", False):
                    posts.append(post_content)

        except Exception as e:
            logger.error(f"Failed to scrape blog posts from {base_url}: {e}")

        return posts
