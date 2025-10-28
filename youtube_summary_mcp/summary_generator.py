"""Text summarization for video transcripts."""

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize

    # Download required NLTK data
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)

except ImportError:
    raise ImportError(
        "nltk is required. Install it with: pip install nltk"
    )


logger = logging.getLogger(__name__)


class SummaryGeneratorError(Exception):
    """Exception raised when summarization fails."""

    pass


class SummarizationStrategy(ABC):
    """Abstract base class for summarization strategies."""

    @abstractmethod
    def summarize(self, text: str, ratio: float = 0.3) -> str:
        """
        Summarize text.

        Args:
            text: Text to summarize
            ratio: Summary ratio (0.0 to 1.0)

        Returns:
            Summarized text
        """
        pass


class TFIDFSummarizer(SummarizationStrategy):
    """
    TF-IDF based summarization strategy.

    Uses term frequency-inverse document frequency to identify
    important sentences.
    """

    def __init__(self) -> None:
        """Initialize TF-IDF summarizer."""
        try:
            self.stop_words = set(stopwords.words("english"))
        except Exception as e:
            logger.warning(f"Could not load stopwords: {e}. Using empty set.")
            self.stop_words = set()

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text.

        Args:
            text: Text to preprocess

        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _calculate_word_frequencies(self, text: str) -> dict[str, float]:
        """
        Calculate word frequencies.

        Args:
            text: Text to analyze

        Returns:
            Dictionary of word frequencies
        """
        words = word_tokenize(text.lower())

        # Filter out stopwords and non-alphabetic words
        filtered_words = [
            word
            for word in words
            if word.isalpha() and word not in self.stop_words
        ]

        if not filtered_words:
            return {}

        # Calculate frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Normalize frequencies
        max_freq = max(word_freq.values())
        for word in word_freq:
            word_freq[word] = word_freq[word] / max_freq

        return word_freq

    def _score_sentences(
        self,
        sentences: list[str],
        word_freq: dict[str, float],
    ) -> dict[str, float]:
        """
        Score sentences based on word frequencies.

        Args:
            sentences: List of sentences
            word_freq: Dictionary of word frequencies

        Returns:
            Dictionary of sentence scores
        """
        sent_scores = {}

        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            score = 0

            for word in words:
                if word in word_freq:
                    score += word_freq[word]

            if score > 0:
                sent_scores[sentence] = score

        return sent_scores

    def summarize(self, text: str, ratio: float = 0.3) -> str:
        """
        Summarize text using TF-IDF.

        Args:
            text: Text to summarize
            ratio: Summary ratio (0.0 to 1.0)

        Returns:
            Summarized text
        """
        try:
            # Preprocess text
            text = self._preprocess_text(text)

            # Split into sentences
            sentences = sent_tokenize(text)

            if len(sentences) == 0:
                return ""

            # Calculate word frequencies
            word_freq = self._calculate_word_frequencies(text)

            if not word_freq:
                # If no words extracted, return first sentence
                return sentences[0]

            # Score sentences
            sent_scores = self._score_sentences(sentences, word_freq)

            if not sent_scores:
                return sentences[0]

            # Select top sentences
            num_sentences = max(1, int(len(sentences) * ratio))
            top_sentences = sorted(
                sent_scores.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:num_sentences]

            # Sort by original order
            summary_sentences = sorted(
                top_sentences,
                key=lambda x: sentences.index(x[0]),
            )

            summary = " ".join([sent for sent, _ in summary_sentences])
            return summary

        except Exception as e:
            logger.error(f"Error during summarization: {e}")
            raise SummaryGeneratorError(f"Summarization failed: {str(e)}") from e


class SummaryGenerator:
    """
    Main summary generator class.

    Follows Strategy pattern by accepting different summarization strategies.
    Uses NLTK-based TF-IDF by default.
    """

    def __init__(
        self,
        strategy: Optional[SummarizationStrategy] = None,
    ) -> None:
        """
        Initialize summary generator.

        Args:
            strategy: SummarizationStrategy instance (default: TFIDFSummarizer)
        """
        self.strategy = strategy or TFIDFSummarizer()

    def generate_summary(
        self,
        text: str,
        ratio: float = 0.3,
    ) -> str:
        """
        Generate summary from text.

        Args:
            text: Text to summarize
            ratio: Summary ratio (0.0 to 1.0)

        Returns:
            Summarized text

        Raises:
            SummaryGeneratorError: If summarization fails
        """
        if not text or not text.strip():
            raise SummaryGeneratorError("Input text cannot be empty")

        if not 0.0 <= ratio <= 1.0:
            raise SummaryGeneratorError("Ratio must be between 0.0 and 1.0")

        try:
            logger.info(f"Generating summary with ratio: {ratio}")
            summary = self.strategy.summarize(text, ratio)
            logger.info(f"Summary generated. Length: {len(summary)} characters")
            return summary

        except SummaryGeneratorError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during summarization: {str(e)}"
            logger.error(error_msg)
            raise SummaryGeneratorError(error_msg) from e

    def generate_summary_with_length(
        self,
        text: str,
        length: str = "medium",
    ) -> str:
        """
        Generate summary with predefined length.

        Args:
            text: Text to summarize
            length: Summary length ("short", "medium", "long")

        Returns:
            Summarized text

        Raises:
            SummaryGeneratorError: If summarization fails
        """
        length_ratios = {
            "short": 0.15,
            "medium": 0.30,
            "long": 0.50,
        }

        if length not in length_ratios:
            raise SummaryGeneratorError(
                f"Invalid length. Must be one of {list(length_ratios.keys())}"
            )

        ratio = length_ratios[length]
        return self.generate_summary(text, ratio)

    def extract_key_points(
        self,
        text: str,
        num_points: int = 5,
    ) -> list[str]:
        """
        Extract key points from text.

        Args:
            text: Text to analyze
            num_points: Number of key points to extract

        Returns:
            List of key point sentences
        """
        try:
            sentences = sent_tokenize(text)

            if len(sentences) == 0:
                return []

            # Use TF-IDF to score sentences
            if isinstance(self.strategy, TFIDFSummarizer):
                word_freq = self.strategy._calculate_word_frequencies(text)
                sent_scores = self.strategy._score_sentences(sentences, word_freq)

                if not sent_scores:
                    return sentences[:num_points]

                # Get top sentences
                top_sentences = sorted(
                    sent_scores.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:num_points]

                return [sent for sent, _ in top_sentences]
            else:
                # Fallback: return first N sentences
                return sentences[:num_points]

        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
