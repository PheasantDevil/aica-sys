"""
GitHub API client for AICA-SyS
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import aiohttp
from github import Github

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.github = Github(token) if token else None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_recent_commits(self, repo_name: str, days: int = 7) -> List[Dict]:
        """Get recent commits from a repository"""
        if not self.github:
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            since = datetime.utcnow() - timedelta(days=days)
            
            commits = []
            for commit in repo.get_commits(since=since):
                commits.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "url": commit.html_url
                })
            
            return commits[:50]  # Limit to 50 commits
            
        except Exception as e:
            logger.error(f"Failed to get commits for {repo_name}: {e}")
            return []
    
    async def get_recent_issues(self, repo_name: str, days: int = 7) -> List[Dict]:
        """Get recent issues from a repository"""
        if not self.github:
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            since = datetime.utcnow() - timedelta(days=days)
            
            issues = []
            for issue in repo.get_issues(since=since, state="all"):
                issues.append({
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "labels": [label.name for label in issue.labels],
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "url": issue.html_url
                })
            
            return issues[:30]  # Limit to 30 issues
            
        except Exception as e:
            logger.error(f"Failed to get issues for {repo_name}: {e}")
            return []
    
    async def get_recent_releases(self, repo_name: str, days: int = 30) -> List[Dict]:
        """Get recent releases from a repository"""
        if not self.github:
            return []
        
        try:
            repo = self.github.get_repo(repo_name)
            since = datetime.utcnow() - timedelta(days=days)
            
            releases = []
            for release in repo.get_releases():
                if release.created_at >= since:
                    releases.append({
                        "tag_name": release.tag_name,
                        "name": release.name,
                        "body": release.body,
                        "created_at": release.created_at.isoformat(),
                        "published_at": release.published_at.isoformat() if release.published_at else None,
                        "url": release.html_url,
                        "assets": [asset.name for asset in release.assets]
                    })
            
            return releases[:10]  # Limit to 10 releases
            
        except Exception as e:
            logger.error(f"Failed to get releases for {repo_name}: {e}")
            return []
    
    async def search_repositories(self, query: str, language: str = "typescript") -> List[Dict]:
        """Search for repositories with specific criteria"""
        if not self.github:
            return []
        
        try:
            search_query = f"{query} language:{language}"
            repositories = self.github.search_repositories(search_query, sort="updated")
            
            repos = []
            for repo in repositories[:20]:  # Limit to 20 results
                repos.append({
                    "name": repo.full_name,
                    "description": repo.description,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "updated_at": repo.updated_at.isoformat(),
                    "url": repo.html_url,
                    "topics": repo.get_topics()
                })
            
            return repos
            
        except Exception as e:
            logger.error(f"Failed to search repositories: {e}")
            return []
