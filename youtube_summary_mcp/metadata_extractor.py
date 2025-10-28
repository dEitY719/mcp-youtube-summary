"""Video metadata extraction from YouTube."""

import logging
import re
from typing import Optional
from urllib.request import urlopen
from urllib.error import URLError

try:
    import re
    import json
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
except ImportError:
    raise ImportError("urllib is required (standard library)")


logger = logging.getLogger(__name__)


class MetadataExtractorError(Exception):
    """Exception raised when metadata extraction fails."""

    pass


class MetadataExtractor:
    """
    Extract metadata from YouTube videos.

    Uses YouTube's embedded data (yt-initial-data) for extracting
    video information without requiring API keys.
    """

    def __init__(self) -> None:
        """Initialize metadata extractor."""
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

    @staticmethod
    def extract_video_id(video_url: str) -> str:
        """
        Extract video ID from YouTube URL.

        Args:
            video_url: YouTube URL or video ID

        Returns:
            Video ID

        Raises:
            MetadataExtractorError: If URL is invalid
        """
        # If it looks like a video ID already
        if re.match(r"^[a-zA-Z0-9_-]{11}$", video_url):
            return video_url

        # Extract from URL
        patterns = [
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})",
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)

        raise MetadataExtractorError(f"Could not extract video ID from: {video_url}")

    def get_basic_metadata(self, video_id: str) -> dict:
        """
        Get basic metadata about a video.

        Note: This is a basic implementation that tries to extract
        metadata from the YouTube page. For production use, consider
        using the official YouTube Data API.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video metadata

        Raises:
            MetadataExtractorError: If metadata extraction fails
        """
        try:
            logger.info(f"Extracting metadata for video: {video_id}")

            url = f"https://www.youtube.com/watch?v={video_id}"
            headers = {"User-Agent": self.user_agent}
            request = Request(url, headers=headers)

            # Attempt to fetch page
            try:
                response = urlopen(request, timeout=10)
                html = response.read().decode("utf-8")
            except (URLError, HTTPError) as e:
                logger.error(f"Failed to fetch page for {video_id}: {e}")
                # Return minimal metadata on failure
                return self._get_empty_metadata(video_id)

            # Extract basic metadata using regex
            metadata = self._extract_from_html(html, video_id)
            logger.info(f"Successfully extracted metadata for {video_id}")

            return metadata

        except Exception as e:
            error_msg = f"Failed to extract metadata: {str(e)}"
            logger.error(error_msg)
            raise MetadataExtractorError(error_msg) from e

    @staticmethod
    def _extract_from_html(html: str, video_id: str) -> dict:
        """
        Extract metadata from HTML.

        Args:
            html: HTML content
            video_id: Video ID

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            "video_id": video_id,
            "title": "Unknown",
            "channel": "Unknown",
            "duration": None,
            "view_count": None,
            "upload_date": None,
            "description": "N/A",
        }

        # Extract title
        title_match = re.search(r'"title":"([^"]+)"', html)
        if title_match:
            metadata["title"] = title_match.group(1)

        # Extract channel name
        channel_match = re.search(r'"shortBylineText":{"simpleText":"([^"]+)"}', html)
        if channel_match:
            metadata["channel"] = channel_match.group(1)

        # Extract view count (simplified)
        views_match = re.search(r'"viewCountText":{"simpleText":"([^"]+)"}', html)
        if views_match:
            metadata["view_count"] = views_match.group(1)

        return metadata

    @staticmethod
    def _get_empty_metadata(video_id: str) -> dict:
        """
        Get empty metadata structure.

        Args:
            video_id: Video ID

        Returns:
            Dictionary with empty metadata
        """
        return {
            "video_id": video_id,
            "title": "Unable to retrieve",
            "channel": "Unknown",
            "duration": None,
            "view_count": None,
            "upload_date": None,
            "description": "Metadata could not be retrieved",
        }

    def get_thumbnail_url(self, video_id: str, quality: str = "hq") -> str:
        """
        Get thumbnail URL for a video.

        Args:
            video_id: YouTube video ID
            quality: Thumbnail quality ("sd", "hq", "mq")
                - "sd": https://img.youtube.com/vi/{id}/default.jpg (120x90)
                - "mq": https://img.youtube.com/vi/{id}/mqdefault.jpg (320x180)
                - "hq": https://img.youtube.com/vi/{id}/hqdefault.jpg (480x360)

        Returns:
            Thumbnail URL
        """
        quality_map = {
            "sd": "default",
            "mq": "mqdefault",
            "hq": "hqdefault",
        }

        quality_key = quality_map.get(quality, "hqdefault")
        return f"https://img.youtube.com/vi/{video_id}/{quality_key}.jpg"

    def format_metadata(self, metadata: dict) -> str:
        """
        Format metadata as readable string.

        Args:
            metadata: Metadata dictionary

        Returns:
            Formatted metadata string
        """
        lines = [
            f"Video ID: {metadata.get('video_id', 'N/A')}",
            f"Title: {metadata.get('title', 'N/A')}",
            f"Channel: {metadata.get('channel', 'N/A')}",
            f"Views: {metadata.get('view_count', 'N/A')}",
            f"Upload Date: {metadata.get('upload_date', 'N/A')}",
            f"Description: {metadata.get('description', 'N/A')}",
        ]

        return "\n".join(lines)
