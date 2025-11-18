"""
Social Media Service
Handles automated social media posting for articles and service promotion
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from services.twitter_client import TwitterClient

logger = logging.getLogger(__name__)


class SocialMediaService:
    """Service for managing social media posts"""

    # Default hashtags for TypeScript/JavaScript content
    DEFAULT_HASHTAGS = [
        "#TypeScript",
        "#JavaScript",
        "#プログラミング",
        "#エンジニア",
        "#開発者",
        "#技術記事",
        "#AI自動生成",
    ]

    def __init__(self):
        """Initialize social media service"""
        self.twitter_client: Optional[TwitterClient] = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize social media API clients"""
        try:
            self.twitter_client = TwitterClient()
            logger.info("Social media clients initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize social media clients: {e}")
            logger.warning("Social media posting will be disabled")

    def format_article_tweet(
        self,
        title: str,
        summary: str,
        url: str,
        hashtags: Optional[List[str]] = None,
        max_length: int = 280,
    ) -> str:
        """
        Format article information as a tweet

        Args:
            title: Article title
            summary: Article summary
            url: Article URL
            hashtags: Optional list of hashtags
            max_length: Maximum tweet length (default 280)

        Returns:
            Formatted tweet text
        """
        # Use provided hashtags or default
        tags = hashtags or self.DEFAULT_HASHTAGS

        # Format hashtags
        hashtag_text = " ".join(tags[:3])  # Limit to 3 hashtags

        # Build tweet text
        # Format: Title + Summary (truncated) + URL + Hashtags
        tweet_parts = []

        # Add title (truncate if needed)
        title_max = 100
        if len(title) > title_max:
            title = title[: title_max - 3] + "..."
        tweet_parts.append(f"📝 {title}")

        # Add summary (truncate to fit)
        available_length = (
            max_length
            - len(tweet_parts[0])
            - len(url)
            - len(hashtag_text)
            - 10  # Spaces and newlines
        )
        if available_length > 0:
            if len(summary) > available_length:
                summary = summary[: available_length - 3] + "..."
            tweet_parts.append(summary)

        # Add URL
        tweet_parts.append(url)

        # Add hashtags
        tweet_parts.append(hashtag_text)

        tweet_text = "\n\n".join(tweet_parts)

        # Final length check and truncate if needed
        if len(tweet_text) > max_length:
            # Truncate summary more aggressively
            excess = len(tweet_text) - max_length
            summary_part = tweet_parts[1] if len(tweet_parts) > 1 else ""
            if summary_part:
                new_summary_length = max(0, len(summary_part) - excess - 3)
                if new_summary_length > 0:
                    tweet_parts[1] = summary_part[:new_summary_length] + "..."
                else:
                    tweet_parts.pop(1)  # Remove summary if too short
                tweet_text = "\n\n".join(tweet_parts)

        return tweet_text

    def post_article(
        self,
        title: str,
        summary: str,
        url: str,
        hashtags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Post article to social media platforms

        Args:
            title: Article title
            summary: Article summary
            url: Article URL
            hashtags: Optional list of hashtags

        Returns:
            Dict containing posting results
        """
        results = {
            "success": False,
            "platforms": {},
            "errors": [],
            "posted_at": datetime.now().isoformat(),
        }

        # Format tweet text
        try:
            tweet_text = self.format_article_tweet(title, summary, url, hashtags)
        except Exception as e:
            logger.error(f"Failed to format tweet: {e}")
            results["errors"].append(f"Tweet formatting error: {e}")
            return results

        # Post to Twitter
        if self.twitter_client:
            try:
                twitter_result = self.twitter_client.post_tweet(tweet_text)
                results["platforms"]["twitter"] = twitter_result
                results["success"] = True
                logger.info(f"Article posted to Twitter: {title}")
            except Exception as e:
                error_msg = f"Twitter posting failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["platforms"]["twitter"] = {"success": False, "error": str(e)}
        else:
            logger.warning("Twitter client not available. Skipping Twitter post.")
            results["errors"].append("Twitter client not initialized")

        return results

    def post_service_introduction(
        self, message: str, hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post service introduction message

        Args:
            message: Service introduction message
            hashtags: Optional list of hashtags

        Returns:
            Dict containing posting results
        """
        results = {
            "success": False,
            "platforms": {},
            "errors": [],
            "posted_at": datetime.now().isoformat(),
        }

        # Format message with hashtags
        tags = hashtags or self.DEFAULT_HASHTAGS
        hashtag_text = " ".join(tags[:3])
        tweet_text = f"{message}\n\n{hashtag_text}"

        # Ensure tweet is within limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."

        # Post to Twitter
        if self.twitter_client:
            try:
                twitter_result = self.twitter_client.post_tweet(tweet_text)
                results["platforms"]["twitter"] = twitter_result
                results["success"] = True
                logger.info("Service introduction posted to Twitter")
            except Exception as e:
                error_msg = f"Twitter posting failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["platforms"]["twitter"] = {"success": False, "error": str(e)}
        else:
            logger.warning("Twitter client not available. Skipping Twitter post.")
            results["errors"].append("Twitter client not initialized")

        return results

    def post_trend_info(
        self, trend_title: str, trend_summary: str, url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post trend information

        Args:
            trend_title: Trend title
            trend_summary: Trend summary
            url: Optional URL to trend page

        Returns:
            Dict containing posting results
        """
        # Format trend tweet
        tweet_parts = [f"📊 {trend_title}", trend_summary]

        if url:
            tweet_parts.append(url)

        tweet_parts.append(" ".join(self.DEFAULT_HASHTAGS[:3]))

        tweet_text = "\n\n".join(tweet_parts)

        # Ensure tweet is within limit
        if len(tweet_text) > 280:
            # Truncate summary
            excess = len(tweet_text) - 280
            if len(trend_summary) > excess:
                tweet_parts[1] = (
                    trend_summary[: len(trend_summary) - excess - 3] + "..."
                )
                tweet_text = "\n\n".join(tweet_parts)

        results = {
            "success": False,
            "platforms": {},
            "errors": [],
            "posted_at": datetime.now().isoformat(),
        }

        # Post to Twitter
        if self.twitter_client:
            try:
                twitter_result = self.twitter_client.post_tweet(tweet_text)
                results["platforms"]["twitter"] = twitter_result
                results["success"] = True
                logger.info(f"Trend info posted to Twitter: {trend_title}")
            except Exception as e:
                error_msg = f"Twitter posting failed: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["platforms"]["twitter"] = {"success": False, "error": str(e)}
        else:
            logger.warning("Twitter client not available. Skipping Twitter post.")
            results["errors"].append("Twitter client not initialized")

        return results

    def verify_connections(self) -> Dict[str, bool]:
        """
        Verify connections to social media platforms

        Returns:
            Dict with platform names as keys and connection status as values
        """
        status = {}

        if self.twitter_client:
            try:
                status["twitter"] = self.twitter_client.verify_credentials()
            except Exception as e:
                logger.error(f"Twitter verification failed: {e}")
                status["twitter"] = False
        else:
            status["twitter"] = False

        return status
