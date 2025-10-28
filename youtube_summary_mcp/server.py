"""MCP Server for YouTube Summary."""

import logging

from mcp.server import Server, InitializationOptions, NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
import mcp.types as types

from .transcript_retriever import TranscriptRetriever, TranscriptFetcherError
from .summary_generator import SummaryGenerator, SummaryGeneratorError
from .metadata_extractor import MetadataExtractor, MetadataExtractorError
from .config_manager import get_config


logger = logging.getLogger(__name__)


class YouTubeSummaryServer:
    """
    MCP Server for YouTube video summarization.

    Provides tools for:
    - Fetching transcripts
    - Generating summaries
    - Extracting key points
    - Getting video metadata
    """

    def __init__(self) -> None:
        """Initialize the server."""
        self.config = get_config()
        self.server = Server(self.config.server_name)
        self.transcript_retriever = TranscriptRetriever()
        self.summary_generator = SummaryGenerator()
        self.metadata_extractor = MetadataExtractor()

        # Register tools
        self._register_tools()

        logger.info(
            f"Initialized {self.config.server_name} v{self.config.server_version}"
        )

    def _register_tools(self) -> None:
        """Register all available tools."""

        # Initialize handler is automatically handled by the Server class

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            try:
                if name == "get_transcript":
                    return await self._handle_get_transcript(arguments)
                elif name == "summarize_video":
                    return await self._handle_summarize_video(arguments)
                elif name == "extract_key_points":
                    return await self._handle_extract_key_points(arguments)
                elif name == "get_video_metadata":
                    return await self._handle_get_video_metadata(arguments)
                else:
                    return [
                        TextContent(
                            type="text",
                            text=f"Unknown tool: {name}",
                        )
                    ]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [
                    TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="get_transcript",
                    description="Fetch the transcript of a YouTube video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_url": {
                                "type": "string",
                                "description": (
                                    "YouTube URL or video ID "
                                    "(e.g., https://www.youtube.com/watch?v=VIDEO_ID or VIDEO_ID)"
                                ),
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code (default: en)",
                                "default": "en",
                            },
                        },
                        "required": ["video_url"],
                    },
                ),
                Tool(
                    name="summarize_video",
                    description="Generate a summary of a YouTube video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_url": {
                                "type": "string",
                                "description": (
                                    "YouTube URL or video ID "
                                    "(e.g., https://www.youtube.com/watch?v=VIDEO_ID or VIDEO_ID)"
                                ),
                            },
                            "summary_length": {
                                "type": "string",
                                "description": "Summary length (short, medium, long)",
                                "enum": ["short", "medium", "long"],
                                "default": "medium",
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code (default: en)",
                                "default": "en",
                            },
                        },
                        "required": ["video_url"],
                    },
                ),
                Tool(
                    name="extract_key_points",
                    description="Extract key points from a YouTube video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_url": {
                                "type": "string",
                                "description": (
                                    "YouTube URL or video ID "
                                    "(e.g., https://www.youtube.com/watch?v=VIDEO_ID or VIDEO_ID)"
                                ),
                            },
                            "num_points": {
                                "type": "integer",
                                "description": "Number of key points to extract",
                                "default": 5,
                            },
                            "language": {
                                "type": "string",
                                "description": "Language code (default: en)",
                                "default": "en",
                            },
                        },
                        "required": ["video_url"],
                    },
                ),
                Tool(
                    name="get_video_metadata",
                    description="Get metadata (title, channel, etc.) of a YouTube video",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "video_url": {
                                "type": "string",
                                "description": (
                                    "YouTube URL or video ID "
                                    "(e.g., https://www.youtube.com/watch?v=VIDEO_ID or VIDEO_ID)"
                                ),
                            },
                        },
                        "required": ["video_url"],
                    },
                ),
            ]

    async def _handle_get_transcript(self, arguments: dict) -> list[types.TextContent]:
        """Handle get_transcript tool call."""
        video_url = arguments.get("video_url")
        language = arguments.get("language", "en")

        if not video_url:
            return [TextContent(type="text", text="Error: video_url is required")]

        try:
            logger.info(f"Getting transcript for: {video_url}")
            transcript = self.transcript_retriever.get_transcript(video_url, language)

            if not transcript:
                return [
                    TextContent(
                        type="text",
                        text="No transcript available for this video",
                    )
                ]

            return [TextContent(type="text", text=transcript)]

        except TranscriptFetcherError as e:
            error_msg = f"Failed to fetch transcript: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def _handle_summarize_video(self, arguments: dict) -> list[types.TextContent]:
        """Handle summarize_video tool call."""
        video_url = arguments.get("video_url")
        summary_length = arguments.get("summary_length", "medium")
        language = arguments.get("language", "en")

        if not video_url:
            return [TextContent(type="text", text="Error: video_url is required")]

        try:
            logger.info(f"Summarizing video: {video_url}")

            # Get transcript
            transcript = self.transcript_retriever.get_transcript(video_url, language)

            if not transcript:
                return [
                    TextContent(
                        type="text",
                        text="No transcript available for this video",
                    )
                ]

            # Generate summary
            summary = self.summary_generator.generate_summary_with_length(
                transcript, summary_length
            )

            if not summary:
                return [
                    TextContent(
                        type="text",
                        text="Could not generate summary from transcript",
                    )
                ]

            return [TextContent(type="text", text=summary)]

        except (TranscriptFetcherError, SummaryGeneratorError) as e:
            error_msg = f"Failed to summarize video: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def _handle_extract_key_points(self, arguments: dict) -> list[types.TextContent]:
        """Handle extract_key_points tool call."""
        video_url = arguments.get("video_url")
        num_points = arguments.get("num_points", 5)
        language = arguments.get("language", "en")

        if not video_url:
            return [TextContent(type="text", text="Error: video_url is required")]

        try:
            logger.info(f"Extracting key points from: {video_url}")

            # Get transcript
            transcript = self.transcript_retriever.get_transcript(video_url, language)

            if not transcript:
                return [
                    TextContent(
                        type="text",
                        text="No transcript available for this video",
                    )
                ]

            # Extract key points
            key_points = self.summary_generator.extract_key_points(
                transcript, num_points
            )

            if not key_points:
                return [
                    TextContent(
                        type="text",
                        text="Could not extract key points from transcript",
                    )
                ]

            formatted_points = "\n".join(
                [f"{i + 1}. {point}" for i, point in enumerate(key_points)]
            )

            return [TextContent(type="text", text=formatted_points)]

        except TranscriptFetcherError as e:
            error_msg = f"Failed to extract key points: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def _handle_get_video_metadata(self, arguments: dict) -> list[types.TextContent]:
        """Handle get_video_metadata tool call."""
        video_url = arguments.get("video_url")

        if not video_url:
            return [TextContent(type="text", text="Error: video_url is required")]

        try:
            logger.info(f"Getting metadata for: {video_url}")

            # Extract video ID
            video_id = self.metadata_extractor.extract_video_id(video_url)

            # Get metadata
            metadata = self.metadata_extractor.get_basic_metadata(video_id)

            # Format metadata
            formatted = self.metadata_extractor.format_metadata(metadata)

            return [TextContent(type="text", text=formatted)]

        except MetadataExtractorError as e:
            error_msg = f"Failed to get metadata: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def run(self) -> None:
        """Run the server using stdio transport."""
        logger.info("Starting YouTube Summary MCP Server")

        # Create notification options (all features disabled by default)
        notification_options = NotificationOptions()

        # Get server capabilities
        capabilities = self.server.get_capabilities(
            notification_options=notification_options,
            experimental_capabilities={},
        )

        # Create initialization options with server capabilities
        init_options = InitializationOptions(
            server_name=self.config.server_name,
            server_version=self.config.server_version,
            capabilities=capabilities,
        )

        # Run the server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                init_options,
            )


async def create_and_run_server() -> None:
    """Create and run the MCP server."""
    server = YouTubeSummaryServer()
    await server.run()
