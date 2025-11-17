"""
データ収集エージェント
TypeScript関連の情報を様々なソースから収集
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from github import Github
import json
import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class ContentItem:
    """収集したコンテンツアイテム"""

    title: str
    url: str
    content: str
    source: str
    published_at: datetime
    tags: List[str]
    importance_score: float = 0.0
    category: str = "general"
    author: Optional[str] = None
    summary: Optional[str] = None


class DataCollector:
    """データ収集エージェントのメインクラス"""

    def __init__(self, github_token: str):
        self.github = Github(github_token)
        self.session = None

        # TypeScript関連のキーワード
        self.typescript_keywords = [
            "typescript",
            "ts",
            "javascript",
            "js",
            "node",
            "react",
            "vue",
            "angular",
            "nextjs",
            "nuxt",
            "svelte",
            "deno",
            "bun",
            "webpack",
            "vite",
            "esbuild",
            "jest",
            "vitest",
            "cypress",
            "playwright",
            "storybook",
            "tailwind",
            "prisma",
            "tRPC",
            "graphql",
            "apollo",
            "relay",
            "swr",
            "tanstack",
        ]

        # 監視対象のRSSフィード
        self.rss_feeds = [
            "https://dev.to/feed",
            "https://blog.logrocket.com/feed/",
            "https://blog.bitsrc.io/feed",
            "https://blog.risingstack.com/rss/",
            "https://blog.angular.io/feed",
            "https://reactjs.org/feed.xml",
            "https://blog.vuejs.org/feed.xml",
            "https://blog.svelte.dev/feed.xml",
            "https://deno.com/blog/feed",
            "https://bun.sh/feed.xml",
        ]

        # 監視対象のGitHubリポジトリ
        self.github_repos = [
            "microsoft/TypeScript",
            "facebook/react",
            "vuejs/vue",
            "angular/angular",
            "vercel/next.js",
            "nuxt/nuxt",
            "sveltejs/svelte",
            "denoland/deno",
            "oven-sh/bun",
            "microsoft/vscode",
        ]

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def collect_all_data(self) -> List[ContentItem]:
        """全ソースからデータを収集"""
        logger.info("データ収集を開始します...")

        all_items = []

        # 並列でデータ収集を実行
        tasks = [
            self.collect_from_rss_feeds(),
            self.collect_from_github(),
            self.collect_from_tech_blogs(),
            self.collect_from_reddit(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"データ収集エラー: {result}")
                continue
            all_items.extend(result)

        logger.info(f"合計 {len(all_items)} 件のコンテンツを収集しました")
        return all_items

    async def collect_from_rss_feeds(self) -> List[ContentItem]:
        """RSSフィードからデータを収集"""
        logger.info("RSSフィードからデータを収集中...")
        items = []

        for feed_url in self.rss_feeds:
            try:
                async with self.session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)

                        for entry in feed.entries[:10]:  # 最新10件
                            if self._is_typescript_related(
                                entry.title + " " + entry.get("summary", "")
                            ):
                                item = ContentItem(
                                    title=entry.title,
                                    url=entry.link,
                                    content=entry.get("summary", ""),
                                    source=f"RSS: {feed_url}",
                                    published_at=(
                                        datetime(*entry.published_parsed[:6])
                                        if entry.published_parsed
                                        else datetime.now()
                                    ),
                                    tags=self._extract_tags(
                                        entry.title + " " + entry.get("summary", "")
                                    ),
                                    author=entry.get("author", ""),
                                    summary=(
                                        entry.get("summary", "")[:200] + "..."
                                        if len(entry.get("summary", "")) > 200
                                        else entry.get("summary", "")
                                    ),
                                )
                                items.append(item)

            except Exception as e:
                logger.error(f"RSSフィード {feed_url} の収集エラー: {e}")
                continue

        logger.info(f"RSSフィードから {len(items)} 件のコンテンツを収集しました")
        return items

    async def collect_from_github(self) -> List[ContentItem]:
        """GitHubからデータを収集"""
        logger.info("GitHubからデータを収集中...")
        items = []

        try:
            for repo_name in self.github_repos:
                try:
                    repo = self.github.get_repo(repo_name)

                    # 最新のリリースを取得
                    releases = repo.get_releases()[:5]
                    for release in releases:
                        if self._is_typescript_related(
                            release.title + " " + release.body
                        ):
                            item = ContentItem(
                                title=f"{repo_name}: {release.title}",
                                url=release.html_url,
                                content=release.body,
                                source=f"GitHub: {repo_name}",
                                published_at=release.published_at or datetime.now(),
                                tags=self._extract_tags(
                                    release.title + " " + release.body
                                ),
                                author=release.author.login if release.author else None,
                                summary=(
                                    release.body[:200] + "..."
                                    if len(release.body) > 200
                                    else release.body
                                ),
                            )
                            items.append(item)

                    # 最新のIssuesを取得
                    issues = repo.get_issues(state="open", sort="updated")[:10]
                    for issue in issues:
                        if self._is_typescript_related(issue.title + " " + issue.body):
                            item = ContentItem(
                                title=f"{repo_name} Issue: {issue.title}",
                                url=issue.html_url,
                                content=issue.body,
                                source=f"GitHub Issue: {repo_name}",
                                published_at=issue.updated_at,
                                tags=self._extract_tags(issue.title + " " + issue.body),
                                author=issue.user.login if issue.user else None,
                                summary=(
                                    issue.body[:200] + "..."
                                    if len(issue.body) > 200
                                    else issue.body
                                ),
                            )
                            items.append(item)

                except Exception as e:
                    logger.error(f"GitHubリポジトリ {repo_name} の収集エラー: {e}")
                    continue

        except Exception as e:
            logger.error(f"GitHub収集エラー: {e}")

        logger.info(f"GitHubから {len(items)} 件のコンテンツを収集しました")
        return items

    async def collect_from_tech_blogs(self) -> List[ContentItem]:
        """技術ブログからデータを収集"""
        logger.info("技術ブログからデータを収集中...")
        items = []

        # 監視対象の技術ブログ
        tech_blogs = [
            "https://blog.logrocket.com/tag/typescript/",
            "https://blog.bitsrc.io/tag/typescript/",
            "https://blog.risingstack.com/tag/typescript/",
            "https://dev.to/t/typescript",
            "https://medium.com/tag/typescript",
        ]

        for blog_url in tech_blogs:
            try:
                async with self.session.get(blog_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, "html.parser")

                        # 記事リンクを抽出
                        article_links = soup.find_all("a", href=True)
                        for link in article_links[:10]:  # 最新10件
                            href = link.get("href")
                            if href and self._is_article_url(href):
                                full_url = urljoin(blog_url, href)

                                # 記事の詳細を取得
                                article_item = await self._scrape_article(full_url)
                                if article_item and self._is_typescript_related(
                                    article_item.title + " " + article_item.content
                                ):
                                    article_item.source = (
                                        f"Tech Blog: {urlparse(blog_url).netloc}"
                                    )
                                    items.append(article_item)

            except Exception as e:
                logger.error(f"技術ブログ {blog_url} の収集エラー: {e}")
                continue

        logger.info(f"技術ブログから {len(items)} 件のコンテンツを収集しました")
        return items

    async def collect_from_reddit(self) -> List[ContentItem]:
        """Redditからデータを収集"""
        logger.info("Redditからデータを収集中...")
        items = []

        # TypeScript関連のSubreddit
        subreddits = [
            "r/typescript",
            "r/javascript",
            "r/reactjs",
            "r/vuejs",
            "r/angular",
            "r/node",
            "r/webdev",
        ]

        for subreddit in subreddits:
            try:
                url = f"https://www.reddit.com/{subreddit}/hot.json?limit=10"
                async with self.session.get(
                    url, headers={"User-Agent": "AICA-SyS/1.0"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for post in data["data"]["children"]:
                            post_data = post["data"]
                            if self._is_typescript_related(
                                post_data["title"] + " " + post_data.get("selftext", "")
                            ):
                                item = ContentItem(
                                    title=post_data["title"],
                                    url=f"https://reddit.com{post_data['permalink']}",
                                    content=post_data.get("selftext", ""),
                                    source=f"Reddit: {subreddit}",
                                    published_at=datetime.fromtimestamp(
                                        post_data["created_utc"]
                                    ),
                                    tags=self._extract_tags(
                                        post_data["title"]
                                        + " "
                                        + post_data.get("selftext", "")
                                    ),
                                    author=post_data.get("author", ""),
                                    summary=(
                                        post_data.get("selftext", "")[:200] + "..."
                                        if len(post_data.get("selftext", "")) > 200
                                        else post_data.get("selftext", "")
                                    ),
                                )
                                items.append(item)

            except Exception as e:
                logger.error(f"Reddit {subreddit} の収集エラー: {e}")
                continue

        logger.info(f"Redditから {len(items)} 件のコンテンツを収集しました")
        return items

    async def _scrape_article(self, url: str) -> Optional[ContentItem]:
        """記事の詳細をスクレイピング"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")

                    # タイトルを抽出
                    title = soup.find("h1") or soup.find("title")
                    title_text = title.get_text().strip() if title else "No Title"

                    # 本文を抽出
                    article_content = ""
                    for tag in soup.find_all(["p", "div", "article"]):
                        if tag.get_text().strip():
                            article_content += tag.get_text().strip() + " "

                    return ContentItem(
                        title=title_text,
                        url=url,
                        content=article_content,
                        source="Scraped Article",
                        published_at=datetime.now(),
                        tags=self._extract_tags(title_text + " " + article_content),
                        summary=(
                            article_content[:200] + "..."
                            if len(article_content) > 200
                            else article_content
                        ),
                    )
        except Exception as e:
            logger.error(f"記事スクレイピングエラー {url}: {e}")
            return None

    def _is_typescript_related(self, text: str) -> bool:
        """TypeScript関連のコンテンツかどうかを判定"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.typescript_keywords)

    def _is_article_url(self, url: str) -> bool:
        """記事URLかどうかを判定"""
        article_patterns = [
            r"/blog/",
            r"/article/",
            r"/post/",
            r"/news/",
            r"/\d{4}/\d{2}/",  # 日付パターン
        ]
        return any(re.search(pattern, url) for pattern in article_patterns)

    def _extract_tags(self, text: str) -> List[str]:
        """テキストからタグを抽出"""
        text_lower = text.lower()
        found_tags = []

        for keyword in self.typescript_keywords:
            if keyword in text_lower:
                found_tags.append(keyword)

        # 追加のタグパターン
        tag_patterns = [
            r"#(\w+)",  # ハッシュタグ
            r"@(\w+)",  # メンション
        ]

        for pattern in tag_patterns:
            matches = re.findall(pattern, text_lower)
            found_tags.extend(matches)

        return list(set(found_tags))  # 重複を削除


# 使用例
async def main():
    """データ収集の実行例"""
    github_token = "your_github_token_here"

    async with DataCollector(github_token) as collector:
        items = await collector.collect_all_data()

        print(f"収集したコンテンツ数: {len(items)}")
        for item in items[:5]:  # 最初の5件を表示
            print(f"- {item.title} ({item.source})")
            print(f"  URL: {item.url}")
            print(f"  Tags: {', '.join(item.tags)}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
