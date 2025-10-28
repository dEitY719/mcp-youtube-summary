"""Tests for transcript_retriever module."""

import pytest

from youtube_summary_mcp.transcript_retriever import (
    TranscriptRetriever,
    TranscriptFetcherError,
)


class TestTranscriptRetriever:
    """Test cases for TranscriptRetriever class."""

    def test_extract_video_id_from_full_url(self) -> None:
        """Test extracting video ID from full YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = TranscriptRetriever.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_short_url(self) -> None:
        """Test extracting video ID from shortened URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = TranscriptRetriever.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_from_direct_id(self) -> None:
        """Test that direct video ID is recognized."""
        video_id = "dQw4w9WgXcQ"
        result = TranscriptRetriever.extract_video_id(video_id)
        assert result == video_id

    def test_extract_video_id_from_invalid_url(self) -> None:
        """Test that invalid URL raises error."""
        with pytest.raises(TranscriptFetcherError):
            TranscriptRetriever.extract_video_id("https://example.com")

    def test_extract_video_id_from_invalid_format(self) -> None:
        """Test that invalid video ID raises error."""
        with pytest.raises(TranscriptFetcherError):
            TranscriptRetriever.extract_video_id("invalid_video_id")

    def test_transcript_retriever_initialization(self) -> None:
        """Test TranscriptRetriever initialization."""
        retriever = TranscriptRetriever()
        assert retriever is not None
        assert retriever.provider is not None
