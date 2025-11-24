"""
Twitter API Client
Handles Twitter/X API v2 integration for automated social media posting
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

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
        bearer_token_raw = os.getenv("TWITTER_BEARER_TOKEN")
        
        # Clean and validate bearer token (strip whitespace, remove empty strings)
        if bearer_token_raw:
            self.bearer_token = bearer_token_raw.strip()
            if not self.bearer_token:  # Empty string after stripping
                self.bearer_token = None
        else:
            self.bearer_token = None

        # Debug: Log which credentials are available (without exposing values)
        has_bearer = bool(self.bearer_token)
        has_oauth1 = all([self.api_key, self.api_secret, self.access_token, self.access_token_secret])
        logger.debug(
            f"Twitter credentials check: bearer_token={has_bearer} (length={len(self.bearer_token) if self.bearer_token else 0}), "
            f"oauth1_complete={has_oauth1}"
        )

        # Validate credentials
        if not self.bearer_token and not all(
            [self.api_key, self.api_secret, self.access_token, self.access_token_secret]
        ):
            missing = []
            if not self.bearer_token:
                missing.append("TWITTER_BEARER_TOKEN")
            if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                oauth1_missing = []
                if not self.api_key:
                    oauth1_missing.append("TWITTER_API_KEY")
                if not self.api_secret:
                    oauth1_missing.append("TWITTER_API_SECRET")
                if not self.access_token:
                    oauth1_missing.append("TWITTER_ACCESS_TOKEN")
                if not self.access_token_secret:
                    oauth1_missing.append("TWITTER_ACCESS_TOKEN_SECRET")
                if oauth1_missing:
                    missing.extend(oauth1_missing)
            raise ValueError(
                f"Twitter API credentials not set. Missing: {', '.join(missing)}. "
                "Set TWITTER_BEARER_TOKEN or TWITTER_API_KEY/SECRET/ACCESS_TOKEN/SECRET"
            )

        # Initialize tweepy client
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize tweepy v2 client"""
        try:
            # Validate bearer_token is not empty or whitespace only
            if self.bearer_token and self.bearer_token.strip():
                # Use Bearer Token (OAuth 2.0) - Recommended for v2 API
                # Strip "Bearer " prefix if present
                bearer_token = self.bearer_token.strip()
                if bearer_token.startswith("Bearer "):
                    bearer_token = bearer_token[7:].strip()
                
                # Final validation: bearer_token must not be empty
                if not bearer_token:
                    raise ValueError(
                        "TWITTER_BEARER_TOKEN is set but empty or invalid. "
                        "Please check your environment variable."
                    )
                
                logger.debug(f"Initializing Twitter client with Bearer Token (length: {len(bearer_token)})")
                self.client = tweepy.Client(
                    bearer_token=bearer_token,
                    wait_on_rate_limit=True,
                )
                logger.info("Twitter client initialized with Bearer Token (OAuth 2.0)")
            else:
                # Use OAuth 1.0a (API Key + Secret + Access Token)
                # Validate all OAuth 1.0a credentials are present and not empty
                oauth1_creds = {
                    "TWITTER_API_KEY": self.api_key,
                    "TWITTER_API_SECRET": self.api_secret,
                    "TWITTER_ACCESS_TOKEN": self.access_token,
                    "TWITTER_ACCESS_TOKEN_SECRET": self.access_token_secret,
                }
                
                # Check if all credentials are present and not empty
                missing = [key for key, value in oauth1_creds.items() if not value or not value.strip()]
                if missing:
                    raise ValueError(
                        f"OAuth 1.0a credentials incomplete. Missing or empty: {', '.join(missing)}. "
                        "All of TWITTER_API_KEY, TWITTER_API_SECRET, "
                        "TWITTER_ACCESS_TOKEN, and TWITTER_ACCESS_TOKEN_SECRET are required."
                    )
                
                # Strip whitespace from all OAuth 1.0a credentials
                api_key = self.api_key.strip()
                api_secret = self.api_secret.strip()
                access_token = self.access_token.strip()
                access_token_secret = self.access_token_secret.strip()
                
                logger.debug("Initializing Twitter client with OAuth 1.0a")
                auth = tweepy.OAuth1UserHandler(
                    api_key,
                    api_secret,
                    access_token,
                    access_token_secret,
                )
                api = tweepy.API(auth, wait_on_rate_limit=True)
                # For v2 API, we still use Client but with OAuth 1.0a
                self.client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    wait_on_rate_limit=True,
                )
                logger.info("Twitter client initialized with OAuth 1.0a")
        except ValueError as e:
            logger.error(f"Twitter client configuration error: {e}")
            raise
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
                metrics = {}
                if getattr(tweet.data, "public_metrics", None):
                    try:
                        metrics = dict(tweet.data.public_metrics)
                    except TypeError:
                        metrics = tweet.data.public_metrics.__dict__
                return {
                    "id": tweet.data.id,
                    "text": tweet.data.text,
                    "created_at": (
                        tweet.data.created_at.isoformat()
                        if tweet.data.created_at
                        else None
                    ),
                    "metrics": metrics,
                }
            return None
        except tweepy.TweepyException as exc:
            logger.error(f"Failed to get tweet: {exc}")
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
