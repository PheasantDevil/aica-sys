"""
Information Collection Agent for AICA-SyS
Collects TypeScript ecosystem information from various sources
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from github import Github
from models.collection import CollectionJob, CollectionType, JobStatus
from sqlalchemy.orm import Session
from utils.github_client import GitHubClient
from utils.rss_parser import RSSParser
from utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)


class CollectionAgent:
    """Agent responsible for collecting TypeScript ecosystem information"""
    
    def __init__(self, db: Session, github_token: Optional[str] = None):
        self.db = db
        self.github_client = GitHubClient(github_token) if github_token else None
        self.rss_parser = RSSParser()
        self.web_scraper = WebScraper()
        
        # TypeScript-related sources
        self.sources = {
            "github": {
                "repos": [
                    "microsoft/TypeScript",
                    "facebook/react",
                    "vercel/next.js",
                    "vuejs/vue",
                    "sveltejs/svelte",
                    "solidjs/solid",
                    "remix-run/remix",
                    "withastro/astro"
                ],
                "keywords": ["typescript", "ts", "types", "type-safe"]
            },
            "rss": [
                "https://dev.to/feed/tag/typescript",
                "https://medium.com/feed/tag/typescript",
                "https://zenn.dev/feed?tag=typescript",
                "https://blog.logrocket.com/tag/typescript/feed/",
                "https://blog.bitsrc.io/tag/typescript/feed"
            ],
            "web_scraping": [
                "https://www.typescriptlang.org/news/",
                "https://react.dev/blog",
                "https://nextjs.org/blog",
                "https://svelte.dev/blog"
            ]
        }
    
    async def collect_all(self) -> Dict[str, int]:
        """Collect information from all sources"""
        results = {}
        
        # GitHub collection
        if self.github_client:
            try:
                github_count = await self._collect_github()
                results["github"] = github_count
                logger.info(f"Collected {github_count} items from GitHub")
            except Exception as e:
                logger.error(f"GitHub collection failed: {e}")
                results["github"] = 0
        
        # RSS collection
        try:
            rss_count = await self._collect_rss()
            results["rss"] = rss_count
            logger.info(f"Collected {rss_count} items from RSS feeds")
        except Exception as e:
            logger.error(f"RSS collection failed: {e}")
            results["rss"] = 0
        
        # Web scraping collection
        try:
            web_count = await self._collect_web_scraping()
            results["web_scraping"] = web_count
            logger.info(f"Collected {web_count} items from web scraping")
        except Exception as e:
            logger.error(f"Web scraping collection failed: {e}")
            results["web_scraping"] = 0
        
        return results
    
    async def _collect_github(self) -> int:
        """Collect information from GitHub repositories"""
        job = CollectionJob(
            source="github",
            type=CollectionType.GITHUB,
            status=JobStatus.RUNNING
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            items_collected = 0
            
            for repo_name in self.sources["github"]["repos"]:
                # Get recent commits
                commits = await self.github_client.get_recent_commits(repo_name, days=7)
                for commit in commits:
                    await self._process_github_commit(repo_name, commit)
                    items_collected += 1
                
                # Get recent issues
                issues = await self.github_client.get_recent_issues(repo_name, days=7)
                for issue in issues:
                    await self._process_github_issue(repo_name, issue)
                    items_collected += 1
                
                # Get recent releases
                releases = await self.github_client.get_recent_releases(repo_name, days=30)
                for release in releases:
                    await self._process_github_release(repo_name, release)
                    items_collected += 1
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.items_collected = items_collected
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error(f"GitHub collection failed: {e}")
        
        self.db.commit()
        return job.items_collected
    
    async def _collect_rss(self) -> int:
        """Collect information from RSS feeds"""
        job = CollectionJob(
            source="rss",
            type=CollectionType.RSS,
            status=JobStatus.RUNNING
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            items_collected = 0
            
            for feed_url in self.sources["rss"]:
                feed_data = await self.rss_parser.parse_feed(feed_url)
                for entry in feed_data.get("entries", []):
                    await self._process_rss_entry(entry)
                    items_collected += 1
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.items_collected = items_collected
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error(f"RSS collection failed: {e}")
        
        self.db.commit()
        return job.items_collected
    
    async def _collect_web_scraping(self) -> int:
        """Collect information from web scraping"""
        job = CollectionJob(
            source="web_scraping",
            type=CollectionType.WEB_SCRAPING,
            status=JobStatus.RUNNING
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            items_collected = 0
            
            for url in self.sources["web_scraping"]:
                content = await self.web_scraper.scrape_url(url)
                if content:
                    await self._process_web_content(url, content)
                    items_collected += 1
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.items_collected = items_collected
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error(f"Web scraping collection failed: {e}")
        
        self.db.commit()
        return job.items_collected
    
    async def _process_github_commit(self, repo_name: str, commit: Dict) -> None:
        """Process GitHub commit data"""
        # Store commit information for analysis
        # This would typically store in a raw data table
        pass
    
    async def _process_github_issue(self, repo_name: str, issue: Dict) -> None:
        """Process GitHub issue data"""
        # Store issue information for analysis
        pass
    
    async def _process_github_release(self, repo_name: str, release: Dict) -> None:
        """Process GitHub release data"""
        # Store release information for analysis
        pass
    
    async def _process_rss_entry(self, entry: Dict) -> None:
        """Process RSS entry data"""
        # Store RSS entry information for analysis
        pass
    
    async def _process_web_content(self, url: str, content: str) -> None:
        """Process web scraped content"""
        # Store web content for analysis
        pass
