"""
Twitter API Client
Handles Twitter/X API v2 integration for automated social media posting
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logging.warning("tweepy not installed. Twitter functionality will be disabled.")

logger = logging.getLogger(__name__)


class TwitterClient:
    """Twitter API v2 Client using tweepy"""

    def __init__(self):
        """Initialize Twitter client with API credentials"""
        if not TWEEPY_AVAILABLE:
            raise ImportError(
                "tweepy is not installed. Install it with: pip install tweepy"
            )

        # Twitter API v2 credentials
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        # Validate credentials
        if not self.bearer_token and not all(
            [self.api_key, self.api_secret, self.access_token, self.access_token_secret]
        ):
            raise ValueError(
                "Twitter API credentials not set. "
                "Set TWITTER_BEARER_TOKEN or TWITTER_API_KEY/SECRET/ACCESS_TOKEN/SECRET"
            )

        # Initialize tweepy client
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize tweepy v2 client"""
        try:
            if self.bearer_token:
                # Use Bearer Token (OAuth 2.0) - Recommended for v2 API
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    wait_on_rate_limit=True,
                )
                logger.info("Twitter client initialized with Bearer Token (OAuth 2.0)")
            else:
                # Use OAuth 1.0a (API Key + Secret + Access Token)
                auth = tweepy.OAuth1UserHandler(
                    self.api_key,
                    self.api_secret,
                    self.access_token,
                    self.access_token_secret,
                )
                api = tweepy.API(auth, wait_on_rate_limit=True)
                # For v2 API, we still use Client but with OAuth 1.0a
                self.client = tweepy.Client(
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True,
                )
                logger.info("Twitter client initialized with OAuth 1.0a")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise

    def post_tweet(self, text: str, media_ids: Optional[list] = None) -> Dict[str, Any]:
        """
        Post a tweet using Twitter API v2

        Args:
            text: Tweet text (max 280 characters)
            media_ids: Optional list of media IDs to attach

        Returns:
            Dict containing tweet data and response status

        Raises:
            ValueError: If text exceeds character limit
            Exception: If tweet posting fails
        """
        if not self.client:
            raise RuntimeError("Twitter client not initialized")

        # Validate text length
        if len(text) > 280:
            raise ValueError(f"Tweet text exceeds 280 characters: {len(text)}")

        try:
            # Post tweet using v2 API
            if media_ids:
                response = self.client.create_tweet(text=text, media_ids=media_ids)
            else:
                response = self.client.create_tweet(text=text)

            tweet_data = response.data
            logger.info(f"Tweet posted successfully: {tweet_data.id}")

            return {
                "success": True,
                "tweet_id": tweet_data.id,
                "text": tweet_data.text,
                "created_at": datetime.now().isoformat(),
            }
        except tweepy.TooManyRequests:
            logger.error("Twitter API rate limit exceeded")
            raise Exception("Twitter API rate limit exceeded. Please try again later.")
        except tweepy.Unauthorized:
            logger.error("Twitter API unauthorized. Check credentials.")
            raise Exception("Twitter API unauthorized. Check API credentials.")
        except tweepy.Forbidden:
            logger.error("Twitter API forbidden. Check permissions.")
            raise Exception("Twitter API forbidden. Check account permissions.")
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            raise

    def upload_media(self, file_path: str) -> Optional[str]:
        """
        Upload media file to Twitter

        Args:
            file_path: Path to media file

        Returns:
            Media ID if successful, None otherwise
        """
        if not self.client:
            raise RuntimeError("Twitter client not initialized")

        try:
            # For v2 API, we need to use v1.1 API for media upload
            # This requires OAuth 1.0a credentials
            if not all(
                [
                    self.api_key,
                    self.api_secret,
                    self.access_token,
                    self.access_token_secret,
                ]
            ):
                logger.warning(
                    "Media upload requires OAuth 1.0a credentials. "
                    "Skipping media upload."
                )
                return None

            auth = tweepy.OAuth1UserHandler(
                self.api_key,
                self.api_secret,
                self.access_token,
                self.access_token_secret,
            )
            api_v1 = tweepy.API(auth)

            # Upload media
            media = api_v1.media_upload(file_path)
            logger.info(f"Media uploaded successfully: {media.media_id}")

            return str(media.media_id)
        except Exception as e:
            logger.error(f"Failed to upload media: {e}")
            return None

    def get_tweet(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tweet by ID

        Args:
            tweet_id: Tweet ID

        Returns:
            Tweet data if found, None otherwise
        """
        if not self.client:
            raise RuntimeError("Twitter client not initialized")

        try:
            tweet = self.client.get_tweet(
                id=tweet_id, tweet_fields=["created_at", "public_metrics"]
            )
            if tweet.data:
                return {
                    "id": tweet.data.id,
                    "text": tweet.data.text,
                    "created_at": tweet.data.created_at.isoformat()
                    if tweet.data.created_at
                    else None,
                    "metrics": tweet.data.public_metrics.__dict__
                    if hasattr(tweet.data, "public_metrics")
                    else {},
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get tweet: {e}")
            return None

    def verify_credentials(self) -> bool:
        """
        Verify Twitter API credentials

        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.client:
            return False

        try:
            # Try to get authenticated user
            me = self.client.get_me()
            if me.data:
                logger.info(f"Twitter credentials verified. User: @{me.data.username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Twitter credentials verification failed: {e}")
            return False

