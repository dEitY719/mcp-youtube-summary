"""Transcript retrieval from YouTube videos."""

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urlparse, parse_qs

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    raise ImportError(
        "youtube-transcript-api is required. "
        "Install it with: pip install youtube-transcript-api"
    )


logger = logging.getLogger(__name__)


class TranscriptFetcherError(Exception):
    """Exception raised when transcript fetching fails."""

    pass


class TranscriptProvider(ABC):
    """Abstract base class for transcript providers."""

    @abstractmethod
    def get_transcript(self, video_id: str, language: str = "en") -> str:
        """
        Get transcript for a video.

        Args:
            video_id: YouTube video ID
            language: Language code (default: "en")

        Returns:
            Transcript text

        Raises:
            TranscriptFetcherError: If transcript cannot be retrieved
        """
        pass


class YouTubeTranscriptProvider(TranscriptProvider):
    """
    YouTube transcript provider using youtube-transcript-api.

    Implements Single Responsibility Principle by handling only
    YouTube API interactions.
    """

    def __init__(self) -> None:
        """Initialize YouTube transcript provider."""
        self.formatter = TextFormatter()
        self.api = YouTubeTranscriptApi()

    def get_transcript(self, video_id: str, language: str = "en") -> str:
        """
        Get transcript from YouTube API.

        Args:
            video_id: YouTube video ID
            language: Language code (default: "en")

        Returns:
            Transcript text

        Raises:
            TranscriptFetcherError: If transcript cannot be retrieved
        """
        try:
            logger.info(f"Fetching transcript for video: {video_id}")

            # Try to get transcript in requested language first
            try:
                # Use new API: fetch() (instance method)
                transcript_data = self.api.fetch(
                    video_id,
                    languages=[language],
                )
                logger.info(
                    f"Successfully fetched transcript in {language} for {video_id}"
                )
            except Exception as lang_error:
                # Fallback to English if requested language not available
                logger.warning(
                    f"Could not fetch transcript in {language} for {video_id}: {lang_error}. "
                    "Trying English..."
                )
                transcript_data = self.api.fetch(video_id)
                logger.info(
                    f"Successfully fetched transcript in fallback language for {video_id}"
                )

            # Format transcript as text
            # The new API returns a FetchedTranscript object, not a list
            transcript_text = self.formatter.format_transcript(transcript_data)
            return transcript_text

        except Exception as e:
            error_msg = f"Failed to fetch transcript for video {video_id}: {str(e)}"
            logger.error(error_msg)
            raise TranscriptFetcherError(error_msg) from e


class TranscriptRetriever:
    """
    Main transcript retriever class.

    Follows Dependency Injection principle by accepting a provider.
    Separates URL parsing and validation from transcript fetching.
    """

    def __init__(self, provider: Optional[TranscriptProvider] = None) -> None:
        """
        Initialize transcript retriever.

        Args:
            provider: TranscriptProvider instance (default: YouTubeTranscriptProvider)
        """
        self.provider = provider or YouTubeTranscriptProvider()

    @staticmethod
    def extract_video_id(video_url: str) -> str:
        """
        Extract video ID from various YouTube URL formats.

        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - VIDEO_ID (direct)

        Args:
            video_url: YouTube URL or video ID

        Returns:
            Video ID

        Raises:
            TranscriptFetcherError: If URL is invalid
        """
        try:
            # If it looks like a video ID already (11 characters, alphanumeric + - _)
            if re.match(r"^[a-zA-Z0-9_-]{11}$", video_url):
                return video_url

            # Parse as URL
            parsed_url = urlparse(video_url)

            # Handle youtu.be format
            if "youtu.be" in parsed_url.netloc:
                video_id = parsed_url.path.lstrip("/")
                if video_id:
                    return video_id

            # Handle youtube.com format
            if "youtube.com" in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get("v", [None])[0]
                if video_id:
                    return video_id

            raise TranscriptFetcherError(
                f"Could not extract video ID from URL: {video_url}"
            )

        except TranscriptFetcherError:
            raise
        except Exception as e:
            raise TranscriptFetcherError(
                f"Invalid YouTube URL: {video_url}"
            ) from e

    def get_transcript(
        self,
        video_url: str,
        language: str = "en",
    ) -> str:
        """
        Get transcript for a YouTube video.

        Args:
            video_url: YouTube URL or video ID
            language: Language code (default: "en")

        Returns:
            Transcript text

        Raises:
            TranscriptFetcherError: If transcript cannot be retrieved
        """
        try:
            video_id = self.extract_video_id(video_url)
            logger.info(f"Extracted video ID: {video_id}")

            transcript = self.provider.get_transcript(video_id, language)
            return transcript

        except TranscriptFetcherError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error retrieving transcript: {str(e)}"
            logger.error(error_msg)
            raise TranscriptFetcherError(error_msg) from e
