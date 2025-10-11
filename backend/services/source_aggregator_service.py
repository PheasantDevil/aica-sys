"""
Source Aggregator Service for AICA-SyS
Phase 10-1: Information collection from multiple sources
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

import feedparser
import requests
from sqlalchemy.orm import Session

from models.automated_content import SourceDataDB, SourceType

logger = logging.getLogger(__name__)


class SourceAggregatorService:
    """情報収集・集約サービス"""

    def __init__(self, db: Session):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AICA-SyS Content Automation Bot 1.0'
        })

    async def collect_all_sources(self) -> List[Dict[str, Any]]:
        """全ソースから情報を収集"""
        all_data = []

        # 各ソースから収集
        sources = [
            self._collect_hacker_news(),
            self._collect_dev_to(),
            self._collect_github_trending(),
            self._collect_reddit(),
            self._collect_tech_crunch()
        ]

        for source_data in sources:
            if source_data:
                all_data.extend(source_data)
                # データベースに保存
                self._save_source_data(source_data)

        logger.info(f"Collected {len(all_data)} items from all sources")
        return all_data

    def _collect_hacker_news(self) -> List[Dict[str, Any]]:
        """Hacker News から収集"""
        try:
            # トップストーリーのIDを取得
            response = self.session.get(
                'https://hacker-news.firebaseio.com/v0/topstories.json',
                timeout=10
            )
            response.raise_for_status()
            story_ids = response.json()[:30]  # トップ30件

            stories = []
            for story_id in story_ids:
                try:
                    story_response = self.session.get(
                        f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json',
                        timeout=5
                    )
                    story_data = story_response.json()

                    if story_data and story_data.get('type') == 'story':
                        stories.append({
                            'source_type': SourceType.HACKER_NEWS,
                            'source_url': story_data.get('url', ''),
                            'title': story_data.get('title', ''),
                            'score': story_data.get('score', 0),
                            'metadata': {
                                'hn_id': story_id,
                                'by': story_data.get('by', ''),
                                'time': story_data.get('time', 0),
                                'descendants': story_data.get('descendants', 0)
                            }
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch HN story {story_id}: {e}")
                    continue

            logger.info(f"Collected {len(stories)} stories from Hacker News")
            return stories

        except Exception as e:
            logger.error(f"Failed to collect from Hacker News: {e}")
            return []

    def _collect_dev_to(self) -> List[Dict[str, Any]]:
        """Dev.to から収集"""
        try:
            response = self.session.get(
                'https://dev.to/api/articles',
                params={'per_page': 20, 'top': 7},  # 週間トップ20件
                timeout=10
            )
            response.raise_for_status()
            articles = response.json()

            collected = []
            for article in articles:
                collected.append({
                    'source_type': SourceType.DEV_TO,
                    'source_url': article.get('url', ''),
                    'title': article.get('title', ''),
                    'score': article.get('positive_reactions_count', 0),
                    'content': article.get('description', ''),
                    'metadata': {
                        'dev_to_id': article.get('id'),
                        'user': article.get('user', {}).get('username', ''),
                        'published_at': article.get('published_at', ''),
                        'tags': article.get('tag_list', [])
                    }
                })

            logger.info(f"Collected {len(collected)} articles from Dev.to")
            return collected

        except Exception as e:
            logger.error(f"Failed to collect from Dev.to: {e}")
            return []

    def _collect_github_trending(self) -> List[Dict[str, Any]]:
        """GitHub Trending から収集"""
        try:
            # 今日のトレンディングリポジトリ
            response = self.session.get(
                'https://api.github.com/search/repositories',
                params={
                    'q': f'created:>{datetime.now().date()}',
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 15
                },
                timeout=10
            )
            response.raise_for_status()
            repos = response.json().get('items', [])

            collected = []
            for repo in repos:
                collected.append({
                    'source_type': SourceType.GITHUB_TRENDING,
                    'source_url': repo.get('html_url', ''),
                    'title': repo.get('full_name', ''),
                    'score': repo.get('stargazers_count', 0),
                    'content': repo.get('description', ''),
                    'metadata': {
                        'github_id': repo.get('id'),
                        'language': repo.get('language', ''),
                        'topics': repo.get('topics', []),
                        'forks': repo.get('forks_count', 0)
                    }
                })

            logger.info(f"Collected {len(collected)} repos from GitHub")
            return collected

        except Exception as e:
            logger.error(f"Failed to collect from GitHub: {e}")
            return []

    def _collect_reddit(self) -> List[Dict[str, Any]]:
        """Reddit r/programming から収集"""
        try:
            response = self.session.get(
                'https://www.reddit.com/r/programming/hot.json',
                params={'limit': 25},
                timeout=10
            )
            response.raise_for_status()
            posts = response.json().get('data', {}).get('children', [])

            collected = []
            for post in posts:
                post_data = post.get('data', {})
                collected.append({
                    'source_type': SourceType.REDDIT,
                    'source_url': post_data.get('url', ''),
                    'title': post_data.get('title', ''),
                    'score': post_data.get('score', 0),
                    'content': post_data.get('selftext', ''),
                    'metadata': {
                        'reddit_id': post_data.get('id'),
                        'author': post_data.get('author', ''),
                        'subreddit': post_data.get('subreddit', ''),
                        'num_comments': post_data.get('num_comments', 0)
                    }
                })

            logger.info(f"Collected {len(collected)} posts from Reddit")
            return collected

        except Exception as e:
            logger.error(f"Failed to collect from Reddit: {e}")
            return []

    def _collect_tech_crunch(self) -> List[Dict[str, Any]]:
        """Tech Crunch RSS から収集"""
        try:
            feed = feedparser.parse('https://techcrunch.com/feed/')
            entries = feed.entries[:10]  # 最新10件

            collected = []
            for entry in entries:
                collected.append({
                    'source_type': SourceType.TECH_CRUNCH,
                    'source_url': entry.get('link', ''),
                    'title': entry.get('title', ''),
                    'score': 0,  # RSSにはスコアなし
                    'content': entry.get('summary', ''),
                    'metadata': {
                        'published': entry.get('published', ''),
                        'author': entry.get('author', ''),
                        'tags': [tag.term for tag in entry.get('tags', [])]
                    }
                })

            logger.info(f"Collected {len(collected)} articles from Tech Crunch")
            return collected

        except Exception as e:
            logger.error(f"Failed to collect from Tech Crunch: {e}")
            return []

    def _save_source_data(self, source_data: List[Dict[str, Any]]):
        """ソースデータをデータベースに保存"""
        try:
            for data in source_data:
                source_db = SourceDataDB(
                    source_type=data.get('source_type'),
                    source_url=data.get('source_url', ''),
                    title=data.get('title', ''),
                    content=data.get('content'),
                    score=data.get('score'),
                    metadata=data.get('metadata', {})
                )
                self.db.add(source_db)

            self.db.commit()
            logger.info(f"Saved {len(source_data)} source data records")

        except Exception as e:
            logger.error(f"Failed to save source data: {e}")
            self.db.rollback()


def aggregate_sources(db: Session) -> List[Dict[str, Any]]:
    """便利関数: 全ソースから情報を収集"""
    import asyncio
    service = SourceAggregatorService(db)
    return asyncio.run(service.collect_all_sources())

