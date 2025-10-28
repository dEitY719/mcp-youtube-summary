"""Tests for summary_generator module."""

import pytest

from youtube_summary_mcp.summary_generator import (
    SummaryGenerator,
    SummaryGeneratorError,
    TFIDFSummarizer,
)


class TestSummaryGenerator:
    """Test cases for SummaryGenerator class."""

    @pytest.fixture
    def sample_text(self) -> str:
        """Provide sample text for testing."""
        return (
            "The quick brown fox jumps over the lazy dog. "
            "This is a test sentence about animals. "
            "Dogs are known for their loyalty and intelligence. "
            "Foxes are clever animals found in many parts of the world. "
            "The lazy dog is resting under the tree. "
            "Many animals live in the forest and jungle."
        )

    def test_summary_generator_initialization(self) -> None:
        """Test SummaryGenerator initialization."""
        generator = SummaryGenerator()
        assert generator is not None
        assert generator.strategy is not None

    def test_generate_summary_with_valid_text(self, sample_text: str) -> None:
        """Test generating summary with valid text."""
        generator = SummaryGenerator()
        summary = generator.generate_summary(sample_text, ratio=0.5)

        assert summary is not None
        assert len(summary) > 0
        assert len(summary) < len(sample_text)

    def test_generate_summary_with_empty_text(self) -> None:
        """Test generating summary with empty text."""
        generator = SummaryGenerator()

        with pytest.raises(SummaryGeneratorError):
            generator.generate_summary("", ratio=0.3)

    def test_generate_summary_with_invalid_ratio(self, sample_text: str) -> None:
        """Test generating summary with invalid ratio."""
        generator = SummaryGenerator()

        with pytest.raises(SummaryGeneratorError):
            generator.generate_summary(sample_text, ratio=1.5)

    def test_generate_summary_with_length_short(self, sample_text: str) -> None:
        """Test generating short summary."""
        generator = SummaryGenerator()
        summary = generator.generate_summary_with_length(sample_text, "short")

        assert summary is not None
        assert len(summary) > 0

    def test_generate_summary_with_length_medium(self, sample_text: str) -> None:
        """Test generating medium summary."""
        generator = SummaryGenerator()
        summary = generator.generate_summary_with_length(sample_text, "medium")

        assert summary is not None
        assert len(summary) > 0

    def test_generate_summary_with_length_long(self, sample_text: str) -> None:
        """Test generating long summary."""
        generator = SummaryGenerator()
        summary = generator.generate_summary_with_length(sample_text, "long")

        assert summary is not None
        assert len(summary) > 0

    def test_generate_summary_with_invalid_length(self, sample_text: str) -> None:
        """Test generating summary with invalid length."""
        generator = SummaryGenerator()

        with pytest.raises(SummaryGeneratorError):
            generator.generate_summary_with_length(sample_text, "invalid")

    def test_extract_key_points(self, sample_text: str) -> None:
        """Test extracting key points."""
        generator = SummaryGenerator()
        key_points = generator.extract_key_points(sample_text, num_points=3)

        assert len(key_points) > 0
        assert len(key_points) <= 3

    def test_tfidf_summarizer(self, sample_text: str) -> None:
        """Test TFIDFSummarizer."""
        summarizer = TFIDFSummarizer()
        summary = summarizer.summarize(sample_text, ratio=0.5)

        assert summary is not None
        assert len(summary) > 0
