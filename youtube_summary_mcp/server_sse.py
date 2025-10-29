"""MCP Server for YouTube Summary using FastMCP with SSE transport."""

import json
import logging
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .transcript_retriever import TranscriptRetriever, TranscriptFetcherError
from .summary_generator import SummaryGenerator, SummaryGeneratorError
from .metadata_extractor import MetadataExtractor, MetadataExtractorError
from .config_manager import get_config


logger = logging.getLogger(__name__)


def create_server_sse(
    host: Optional[str] = None,
    port: Optional[int] = None,
    sse_path: Optional[str] = None,
) -> FastMCP:
    """
    Create and return a FastMCP server instance for SSE transport.

    Args:
        host: Host to bind to (default: from env MCP_SSE_HOST or 0.0.0.0)
        port: Port to bind to (default: from env MCP_SSE_PORT or 10719)
        sse_path: SSE endpoint path (default: from env MCP_SSE_PATH or /sse)

    Returns:
        FastMCP: Configured server instance
    """
    config = get_config()

    # Get settings from parameters, environment variables, or defaults
    effective_host = host or os.getenv("MCP_SSE_HOST", "0.0.0.0")
    effective_port = port or int(os.getenv("MCP_SSE_PORT", "10719"))
    effective_sse_path = sse_path or os.getenv("MCP_SSE_PATH", "/sse")

    logger.info(
        "Creating SSE server: %s:%d%s",
        effective_host,
        effective_port,
        effective_sse_path,
    )

    server = FastMCP(
        name=config.server_name,
        host=effective_host,
        port=effective_port,
        sse_path=effective_sse_path,
    )

    # Initialize components
    transcript_retriever = TranscriptRetriever()
    summary_generator = SummaryGenerator()
    metadata_extractor = MetadataExtractor()

    logger.info(
        "Initialized %s v%s (SSE transport)",
        config.server_name,
        config.server_version,
    )

    @server.tool()
    def get_transcript(
        video_url: str,
        language: str = "en",
    ) -> str:
        """
        Fetch the transcript of a YouTube video.

        Args:
            video_url: YouTube URL or video ID
            language: Language code (default: en)

        Returns:
            Transcript text
        """
        try:
            logger.info("Getting transcript for: %s", video_url)
            transcript = transcript_retriever.get_transcript(video_url, language)

            if not transcript:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No transcript available for this video",
                    },
                    ensure_ascii=False,
                )

            return json.dumps(
                {
                    "success": True,
                    "transcript": transcript,
                },
                ensure_ascii=False,
            )

        except TranscriptFetcherError as e:
            error_msg = f"Failed to fetch transcript: {str(e)}"
            logger.error(error_msg)
            return json.dumps(
                {
                    "success": False,
                    "error": error_msg,
                },
                ensure_ascii=False,
            )
        except Exception as e:
            logger.error("Unexpected error in get_transcript: %s", str(e))
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                },
                ensure_ascii=False,
            )

    @server.tool()
    def summarize_video(
        video_url: str,
        summary_length: str = "medium",
        language: str = "en",
    ) -> str:
        """
        Generate a summary of a YouTube video.

        Args:
            video_url: YouTube URL or video ID
            summary_length: Summary length (short, medium, long)
            language: Language code (default: en)

        Returns:
            Summary text
        """
        try:
            logger.info("Summarizing video: %s", video_url)

            # Get transcript
            transcript = transcript_retriever.get_transcript(video_url, language)

            if not transcript:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No transcript available for this video",
                    },
                    ensure_ascii=False,
                )

            # Generate summary
            summary = summary_generator.generate_summary_with_length(
                transcript, summary_length
            )

            if not summary:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Could not generate summary from transcript",
                    },
                    ensure_ascii=False,
                )

            return json.dumps(
                {
                    "success": True,
                    "summary": summary,
                    "length": summary_length,
                },
                ensure_ascii=False,
            )

        except (TranscriptFetcherError, SummaryGeneratorError) as e:
            error_msg = f"Failed to summarize video: {str(e)}"
            logger.error(error_msg)
            return json.dumps(
                {
                    "success": False,
                    "error": error_msg,
                },
                ensure_ascii=False,
            )
        except Exception as e:
            logger.error("Unexpected error in summarize_video: %s", str(e))
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                },
                ensure_ascii=False,
            )

    @server.tool()
    def extract_key_points(
        video_url: str,
        num_points: int = 5,
        language: str = "en",
    ) -> str:
        """
        Extract key points from a YouTube video.

        Args:
            video_url: YouTube URL or video ID
            num_points: Number of key points to extract (default: 5)
            language: Language code (default: en)

        Returns:
            Formatted key points
        """
        try:
            logger.info("Extracting key points from: %s", video_url)

            # Get transcript
            transcript = transcript_retriever.get_transcript(video_url, language)

            if not transcript:
                return json.dumps(
                    {
                        "success": False,
                        "error": "No transcript available for this video",
                    },
                    ensure_ascii=False,
                )

            # Extract key points
            key_points = summary_generator.extract_key_points(
                transcript, num_points
            )

            if not key_points:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Could not extract key points from transcript",
                    },
                    ensure_ascii=False,
                )

            return json.dumps(
                {
                    "success": True,
                    "key_points": key_points,
                    "count": len(key_points),
                },
                ensure_ascii=False,
            )

        except TranscriptFetcherError as e:
            error_msg = f"Failed to extract key points: {str(e)}"
            logger.error(error_msg)
            return json.dumps(
                {
                    "success": False,
                    "error": error_msg,
                },
                ensure_ascii=False,
            )
        except Exception as e:
            logger.error("Unexpected error in extract_key_points: %s", str(e))
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                },
                ensure_ascii=False,
            )

    @server.tool()
    def get_video_metadata(
        video_url: str,
    ) -> str:
        """
        Get metadata (title, channel, etc.) of a YouTube video.

        Args:
            video_url: YouTube URL or video ID

        Returns:
            Formatted metadata
        """
        try:
            logger.info("Getting metadata for: %s", video_url)

            # Extract video ID
            video_id = metadata_extractor.extract_video_id(video_url)

            # Get metadata
            metadata = metadata_extractor.get_basic_metadata(video_id)

            # Format metadata
            formatted = metadata_extractor.format_metadata(metadata)

            return json.dumps(
                {
                    "success": True,
                    "metadata": formatted,
                },
                ensure_ascii=False,
            )

        except MetadataExtractorError as e:
            error_msg = f"Failed to get metadata: {str(e)}"
            logger.error(error_msg)
            return json.dumps(
                {
                    "success": False,
                    "error": error_msg,
                },
                ensure_ascii=False,
            )
        except Exception as e:
            logger.error("Unexpected error in get_video_metadata: %s", str(e))
            return json.dumps(
                {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                },
                ensure_ascii=False,
            )

    return server
