# YouTube Summary MCP Server

A powerful MCP (Model Context Protocol) server for summarizing YouTube videos with transcript fetching, intelligent summarization, key point extraction, and metadata retrieval.

## Features

- **Transcript Fetching**: Retrieve transcripts from any YouTube video
- **Intelligent Summarization**: Generate summaries of various lengths (short, medium, long)
- **Key Point Extraction**: Automatically extract key points from video transcripts
- **Video Metadata**: Get video title, channel, view count, and more
- **Multi-language Support**: Support for multiple languages
- **Error Handling**: Comprehensive error handling and logging
- **SOLID Principles**: Well-designed architecture following SOLID principles

## Installation

### Prerequisites

- Python 3.10+
- `uv` package manager

### Setup

1. **Clone the repository** (or navigate to the project directory)

```bash
cd youtube-summary-mcp
```

2. **Create virtual environment and install dependencies**

```bash
uv sync
```

This will install all dependencies including:
- `mcp`: Model Context Protocol
- `youtube-transcript-api`: For fetching YouTube transcripts
- `nltk`: For natural language processing
- `pydantic`: For configuration management

## Usage

### As an MCP Server

To run the server:

```bash
uv run youtube-summary-mcp
```

### Available Tools

The server exposes the following tools:

#### 1. **get_transcript**
Fetch the transcript of a YouTube video.

**Parameters:**
- `video_url` (required): YouTube URL or video ID
- `language` (optional): Language code (default: "en")

**Example:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "language": "en"
}
```

#### 2. **summarize_video**
Generate a summary of a YouTube video.

**Parameters:**
- `video_url` (required): YouTube URL or video ID
- `summary_length` (optional): "short", "medium", or "long" (default: "medium")
- `language` (optional): Language code (default: "en")

**Example:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "summary_length": "medium",
  "language": "en"
}
```

#### 3. **extract_key_points**
Extract key points from a YouTube video's transcript.

**Parameters:**
- `video_url` (required): YouTube URL or video ID
- `num_points` (optional): Number of key points to extract (default: 5)
- `language` (optional): Language code (default: "en")

**Example:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "num_points": 5,
  "language": "en"
}
```

#### 4. **get_video_metadata**
Get metadata about a YouTube video.

**Parameters:**
- `video_url` (required): YouTube URL or video ID

**Example:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

## Configuration

Configuration is managed through environment variables or a `.env` file.

### Available Configuration Options

```bash
# API Configuration
YOUTUBE_API_KEY=your_api_key  # Optional

# Summary Configuration
SUMMARY_LENGTH=medium         # short, medium, or long
SUMMARY_RATIO=0.3            # 0.0 to 1.0

# Language Configuration
DEFAULT_LANGUAGE=en           # Default language for transcripts
SUPPORTED_LANGUAGES=en,ko,es,fr,de,ja,zh  # Comma-separated list

# Rate Limiting
RATE_LIMIT_ENABLED=true      # Enable rate limiting
RATE_LIMIT_REQUESTS=100      # Requests per window
RATE_LIMIT_WINDOW_SECONDS=3600  # Window size in seconds

# Caching
CACHE_ENABLED=true           # Enable caching
CACHE_TTL_SECONDS=86400      # Cache time-to-live (24 hours)

# Logging
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Server Configuration
SERVER_NAME=YouTube Summary MCP
SERVER_VERSION=0.1.0
```

## Project Structure

```
youtube-summary-mcp/
├── youtube_summary_mcp/
│   ├── __init__.py                  # Package initialization
│   ├── config_manager.py            # Configuration management
│   ├── transcript_retriever.py       # Transcript fetching
│   ├── summary_generator.py          # Text summarization
│   ├── metadata_extractor.py         # Video metadata extraction
│   ├── server.py                     # MCP server implementation
│   └── main.py                       # Entry point
├── tests/
│   ├── __init__.py
│   ├── test_config_manager.py
│   ├── test_transcript_retriever.py
│   ├── test_summary_generator.py
│   └── test_metadata_extractor.py
├── pyproject.toml                   # Project configuration
└── README.md                        # This file
```

## Architecture

### SOLID Principles

The project follows SOLID principles:

1. **Single Responsibility Principle (SRP)**
   - Each module has a single, well-defined responsibility
   - `TranscriptRetriever`: Only handles transcript fetching
   - `SummaryGenerator`: Only handles summarization
   - `ConfigManager`: Only handles configuration

2. **Open/Closed Principle (OCP)**
   - Modules are open for extension (strategies pattern)
   - `SummarizationStrategy`: Abstract base for different summarization algorithms
   - `TranscriptProvider`: Abstract base for different transcript sources

3. **Liskov Substitution Principle (LSP)**
   - Subclasses can be substituted for base classes
   - `TFIDFSummarizer` can replace `SummarizationStrategy`
   - `YouTubeTranscriptProvider` can replace `TranscriptProvider`

4. **Interface Segregation Principle (ISP)**
   - Clients depend only on the interfaces they use
   - Small, focused abstract classes

5. **Dependency Inversion Principle (DIP)**
   - Depend on abstractions, not concrete implementations
   - Dependency injection pattern used throughout

## Testing

Run tests using pytest:

```bash
uv run pytest tests/
```

Run tests with coverage:

```bash
uv run pytest tests/ --cov=youtube_summary_mcp
```

Run specific test file:

```bash
uv run pytest tests/test_summary_generator.py -v
```

## Development

### Code Style

The project uses:
- `black` for code formatting
- `ruff` for linting
- `mypy` for type checking

Format code:
```bash
uv run black youtube_summary_mcp/ tests/
```

Lint code:
```bash
uv run ruff check youtube_summary_mcp/ tests/
```

Check types:
```bash
uv run mypy youtube_summary_mcp/
```

## Supported URL Formats

The server supports multiple YouTube URL formats:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- Direct video ID: `VIDEO_ID`

## Error Handling

The server provides detailed error messages for:
- Invalid YouTube URLs
- Unavailable transcripts (private videos, live streams)
- Transcript fetching failures
- Summarization errors
- API errors

All errors are logged with context information for debugging.

## Performance

### Summarization

- **TF-IDF Algorithm**: Fast, efficient text-based summarization
- **Ratio-based**: Configurable summary length (0.0-1.0 of original text)
- **Keyword Extraction**: Identifies important terms and sentences

### Caching

Optional caching of transcripts (24 hours by default) to reduce API calls.

## Limitations

- Requires video to have a transcript available
- YouTube API rate limits may apply (100+ requests per hour recommended)
- Transcripts availability depends on YouTube's caption availability
- Metadata extraction may be limited without YouTube Data API key

## Contributing

Contributions are welcome! Please ensure:
- Code follows SOLID principles
- Tests are included for new features
- Code is properly typed
- Documentation is updated

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
1. Check existing documentation
2. Review error logs
3. Open an issue on GitHub (if applicable)

## Changelog

### Version 0.1.0 (Initial Release)
- Basic transcript fetching
- TF-IDF based summarization
- Key point extraction
- Video metadata retrieval
- Configuration management
- Comprehensive error handling
- Full test coverage
