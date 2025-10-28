"""Tests for metadata_extractor module."""

import pytest

from youtube_summary_mcp.metadata_extractor import (
    MetadataExtractor,
    MetadataExtractorError,
)


class TestMetadataExtractor:
    """Test cases for MetadataExtractor class."""

    @pytest.fixture
    def extractor(self) -> MetadataExtractor:
        """Provide MetadataExtractor instance."""
        return MetadataExtractor()

    def test_metadata_extractor_initialization(self, extractor: MetadataExtractor) -> None:
        """Test MetadataExtractor initialization."""
        assert extractor is not None
        assert extractor.user_agent is not None

    def test_extract_video_id_from_full_url(self, extractor: MetadataExtractor) -> None:
        """Test extracting video ID from full URL."""
        url = "https://www.youtube.com/watch?v=HQU2vbsbXkU"
        video_id = extractor.extract_video_id(url)
        assert video_id == "HQU2vbsbXkU"

    def test_extract_video_id_from_short_url(self, extractor: MetadataExtractor) -> None:
        """Test extracting video ID from short URL."""
        url = "https://youtu.be/HQU2vbsbXkU"
        video_id = extractor.extract_video_id(url)
        assert video_id == "HQU2vbsbXkU"

    def test_extract_video_id_from_embed_url(self, extractor: MetadataExtractor) -> None:
        """Test extracting video ID from embed URL."""
        url = "https://www.youtube.com/embed/HQU2vbsbXkU"
        video_id = extractor.extract_video_id(url)
        assert video_id == "HQU2vbsbXkU"

    def test_extract_video_id_from_direct_id(self, extractor: MetadataExtractor) -> None:
        """Test extracting direct video ID."""
        video_id = "HQU2vbsbXkU"
        result = extractor.extract_video_id(video_id)
        assert result == video_id

    def test_extract_video_id_from_invalid_url(self, extractor: MetadataExtractor) -> None:
        """Test extracting from invalid URL."""
        with pytest.raises(MetadataExtractorError):
            extractor.extract_video_id("https://example.com")

    def test_get_thumbnail_url(self, extractor: MetadataExtractor) -> None:
        """Test getting thumbnail URL."""
        video_id = "HQU2vbsbXkU"

        # Test standard quality
        url_sd = extractor.get_thumbnail_url(video_id, "sd")
        assert "default.jpg" in url_sd
        assert video_id in url_sd

        # Test medium quality
        url_mq = extractor.get_thumbnail_url(video_id, "mq")
        assert "mqdefault.jpg" in url_mq
        assert video_id in url_mq

        # Test high quality
        url_hq = extractor.get_thumbnail_url(video_id, "hq")
        assert "hqdefault.jpg" in url_hq
        assert video_id in url_hq

    def test_format_metadata(self, extractor: MetadataExtractor) -> None:
        """Test formatting metadata."""
        metadata = {
            "video_id": "HQU2vbsbXkU",
            "title": "Test Video",
            "channel": "Test Channel",
            "views": "1000",
            "upload_date": "2023-01-01",
            "description": "Test Description",
        }

        formatted = extractor.format_metadata(metadata)
        assert "HQU2vbsbXkU" in formatted
        assert "Test Video" in formatted
        assert "Test Channel" in formatted
