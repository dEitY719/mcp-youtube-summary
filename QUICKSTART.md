# Quick Start Guide

## Installation & Setup

### 1. Prerequisites
- Python 3.10+
- `uv` package manager installed

### 2. Install Dependencies

```bash
cd youtube-summary-mcp
uv sync
```

This installs:
- `mcp` - Model Context Protocol
- `youtube-transcript-api` - YouTube transcript fetching
- `nltk` - Natural language processing
- `pydantic` - Configuration management

### 3. (Optional) Configure Settings

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```bash
SUMMARY_LENGTH=medium          # short, medium, or long
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR, CRITICAL
DEFAULT_LANGUAGE=en           # Language for transcripts
```

## Running the Server

### Start the Server

```bash
uv run youtube-summary-mcp
```

You should see output like:
```
2024-01-15 10:30:45,123 - youtube_summary_mcp.server - INFO - Initialized YouTube Summary MCP v0.1.0
2024-01-15 10:30:45,456 - youtube_summary_mcp.server - INFO - Starting YouTube Summary MCP Server
```

The server is now running and ready to accept MCP tool calls.

## Using the Tools

### Tool 1: Get Transcript

Fetch the raw transcript from a YouTube video:

```python
# Call the tool with:
{
  "tool": "get_transcript",
  "arguments": {
    "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
    "language": "en"
  }
}
```

### Tool 2: Summarize Video

Get an intelligent summary of a video:

```python
{
  "tool": "summarize_video",
  "arguments": {
    "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
    "summary_length": "medium",
    "language": "en"
  }
}
```

**Summary lengths:**
- `short`: ~20% of original text
- `medium`: ~35% of original text
- `long`: ~50% of original text

### Tool 3: Extract Key Points

Get the most important sentences from a video:

```python
{
  "tool": "extract_key_points",
  "arguments": {
    "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU",
    "num_points": 5,
    "language": "en"
  }
}
```

### Tool 4: Get Video Metadata

Get basic info about a video (title, channel, views, etc.):

```python
{
  "tool": "get_video_metadata",
  "arguments": {
    "video_url": "https://www.youtube.com/watch?v=HQU2vbsbXkU"
  }
}
```

## Supported YouTube URL Formats

All tools accept any of these URL formats:

```
https://www.youtube.com/watch?v=VIDEO_ID
https://youtu.be/VIDEO_ID
https://www.youtube.com/embed/VIDEO_ID
VIDEO_ID                                    (just the ID)
```

Example with short URL:
```python
{
  "tool": "summarize_video",
  "arguments": {
    "video_url": "youtu.be/HQU2vbsbXkU"
  }
}
```

## Testing

Run the test suite to verify everything works:

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_summary_generator.py -v

# Run with coverage report
uv run pytest tests/ --cov=youtube_summary_mcp
```

## Common Workflows

### Workflow 1: Summarize a YouTube Tutorial

```bash
# User: "Summarize this Python tutorial for me"
# 1. Extract video ID from URL
# 2. Call get_transcript_tool
# 3. Call summarize_video_tool with summary_length="medium"
# 4. Return summary to user
```

### Workflow 2: Get Key Takeaways

```bash
# User: "What are the main points from this lecture?"
# 1. Call get_transcript_tool
# 2. Call extract_key_points (5 points)
# 3. Return formatted list to user
```

### Workflow 3: Learn About a Video

```bash
# User: "Tell me about this video"
# 1. Call get_video_metadata
# 2. Call summarize_video with summary_length="short"
# 3. Return metadata + summary
```

## Troubleshooting

### Issue: "No transcript available"
- **Cause**: Video has no captions/transcript
- **Solution**: Try another video with captions enabled

### Issue: ImportError with youtube-transcript-api
- **Cause**: Package not installed
- **Solution**: `uv sync` or `uv pip install youtube-transcript-api`

### Issue: Server won't start
- **Cause**: Port already in use or missing dependencies
- **Solution**:
  1. Check dependencies: `uv sync`
  2. Check logs: Look for errors in console
  3. Verify Python version: `python3 --version` (need 3.10+)

### Issue: Slow summarization
- **Cause**: Large transcript with NLTK processing
- **Solution**: Use smaller summary_ratio or shorter summary_length

## Next Steps

1. **Read the full documentation**: See `README.md`
2. **Explore the code**: Check `DEVELOPMENT.md` for architecture details
3. **Customize**: Modify configuration in `.env`
4. **Extend**: Add new features following the existing patterns
5. **Test**: Run tests and add new test cases

## Project Structure

```
youtube-summary-mcp/
├── youtube_summary_mcp/          # Main package
│   ├── server.py                 # MCP server & tools
│   ├── transcript_retriever.py    # Fetch transcripts
│   ├── summary_generator.py       # Summarization logic
│   ├── metadata_extractor.py      # Get video info
│   ├── config_manager.py          # Configuration
│   └── main.py                    # Entry point
├── tests/                         # Test suite
├── pyproject.toml                 # Project configuration
├── README.md                      # Full documentation
├── DEVELOPMENT.md                 # Development guide
└── QUICKSTART.md                  # This file
```

## Key Features

✅ **Easy to Use**: Simple tool-based interface
✅ **Well Tested**: Unit tests for all modules
✅ **SOLID Design**: Professional code architecture
✅ **Configurable**: Environment-based configuration
✅ **Documented**: Comprehensive docs & guides
✅ **Extensible**: Easy to add new features
✅ **Error Handling**: Graceful error management
✅ **Type Safe**: Full type hints throughout

## Support

- See `README.md` for detailed documentation
- See `DEVELOPMENT.md` for technical details
- Check test files for usage examples
- Review module docstrings for API details

---

Happy summarizing! 🎥📝
