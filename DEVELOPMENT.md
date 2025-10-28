# Development Guide

## Overview

This document provides guidelines for developing and extending the YouTube Summary MCP Server.

## Architecture Overview

### Module Responsibilities

#### `config_manager.py`
- **Responsibility**: Centralized configuration management
- **Pattern**: Singleton pattern with dependency injection
- **Key Classes**:
  - `ConfigManager`: Pydantic-based configuration with validation
  - `get_config()`: Returns singleton instance
  - `set_config()`: Sets global configuration (useful for testing)

#### `transcript_retriever.py`
- **Responsibility**: YouTube transcript fetching and URL parsing
- **Pattern**: Strategy pattern + Dependency Injection
- **Key Classes**:
  - `TranscriptProvider`: Abstract base for different providers
  - `YouTubeTranscriptProvider`: Concrete implementation using youtube-transcript-api
  - `TranscriptRetriever`: Main facade class
- **Features**:
  - Multiple URL format support
  - Language fallback mechanism
  - Comprehensive error handling

#### `summary_generator.py`
- **Responsibility**: Text summarization and key point extraction
- **Pattern**: Strategy pattern for different algorithms
- **Key Classes**:
  - `SummarizationStrategy`: Abstract base for algorithms
  - `TFIDFSummarizer`: TF-IDF based implementation
  - `SummaryGenerator`: Main facade with multiple output options
- **Features**:
  - Configurable summary ratio
  - Predefined length templates (short, medium, long)
  - Key point extraction
  - Stopword filtering

#### `metadata_extractor.py`
- **Responsibility**: Video metadata extraction
- **Key Classes**:
  - `MetadataExtractor`: Extracts metadata without API key
- **Features**:
  - Multiple URL format support
  - Thumbnail URL generation
  - Metadata formatting

#### `server.py`
- **Responsibility**: MCP server implementation
- **Pattern**: Tool registry pattern
- **Key Classes**:
  - `YouTubeSummaryServer`: Main server class
- **Tools**:
  - `get_transcript`: Fetch transcript
  - `summarize_video`: Generate summary
  - `extract_key_points`: Extract key points
  - `get_video_metadata`: Get video metadata

#### `main.py`
- **Responsibility**: Entry point and CLI
- **Key Functions**:
  - `main()`: Main entry point
  - `setup_logging()`: Configure logging

## Design Patterns Used

### 1. Singleton Pattern
- **Location**: `ConfigManager` via `get_config()`
- **Purpose**: Ensure single configuration instance
- **Benefit**: Global state management with control

### 2. Strategy Pattern
- **Location**: `SummarizationStrategy`, `TranscriptProvider`
- **Purpose**: Allow different implementations
- **Benefit**: Easy to extend with new algorithms/providers

### 3. Dependency Injection
- **Location**: Throughout all classes
- **Purpose**: Decouple dependencies
- **Benefit**: Testability and flexibility

### 4. Facade Pattern
- **Location**: `TranscriptRetriever`, `SummaryGenerator`
- **Purpose**: Simple interface for complex subsystems
- **Benefit**: Easy to use, hides implementation details

### 5. Template Method Pattern
- **Location**: `TranscriptProvider`, `SummarizationStrategy`
- **Purpose**: Define algorithm outline, let subclasses fill in details
- **Benefit**: Code reuse and consistency

## SOLID Principles Compliance

### Single Responsibility Principle
Each class has ONE reason to change:
- `ConfigManager` only changes if configuration structure changes
- `TranscriptRetriever` only changes if transcript fetching changes
- `SummaryGenerator` only changes if summarization algorithm changes

### Open/Closed Principle
Classes are open for extension, closed for modification:
- Add new `SummarizationStrategy` without modifying `SummaryGenerator`
- Add new `TranscriptProvider` without modifying `TranscriptRetriever`

### Liskov Substitution Principle
Subclasses can be used interchangeably:
```python
# Can switch implementations without breaking code
provider: TranscriptProvider = YouTubeTranscriptProvider()
strategy: SummarizationStrategy = TFIDFSummarizer()
```

### Interface Segregation Principle
Clients depend only on interfaces they use:
- `TranscriptRetriever` uses `TranscriptProvider` interface
- `SummaryGenerator` uses `SummarizationStrategy` interface

### Dependency Inversion Principle
Depend on abstractions, not concretions:
```python
# Good: Depend on interface
retriever = TranscriptRetriever(provider=custom_provider)

# Bad: Depend on concrete implementation
retriever = TranscriptRetriever(YouTubeTranscriptProvider())
```

## Testing Strategy

### Test Structure
- Unit tests for each module
- Mock external dependencies
- Test both success and error cases

### Running Tests
```bash
# All tests
uv run pytest tests/ -v

# Specific file
uv run pytest tests/test_summary_generator.py -v

# With coverage
uv run pytest tests/ --cov=youtube_summary_mcp --cov-report=html

# Specific test
uv run pytest tests/test_summary_generator.py::TestSummaryGenerator::test_generate_summary_with_valid_text -v
```

## Extending the Project

### Adding a New Summarization Algorithm

1. Create a new class inheriting from `SummarizationStrategy`:

```python
# In summary_generator.py

class SpacySummarizer(SummarizationStrategy):
    """spaCy-based summarization."""

    def __init__(self):
        import spacy
        self.nlp = spacy.load("en_core_web_sm")

    def summarize(self, text: str, ratio: float = 0.3) -> str:
        # Implementation using spaCy
        pass
```

2. Use it:

```python
from youtube_summary_mcp.summary_generator import SummaryGenerator, SpacySummarizer

generator = SummaryGenerator(strategy=SpacySummarizer())
summary = generator.generate_summary(text)
```

3. Add tests for the new strategy.

### Adding a New Transcript Provider

1. Create a new class inheriting from `TranscriptProvider`:

```python
# In transcript_retriever.py

class VimeoTranscriptProvider(TranscriptProvider):
    """Vimeo transcript provider."""

    def get_transcript(self, video_id: str, language: str = "en") -> str:
        # Implementation for Vimeo
        pass
```

2. Use it:

```python
from youtube_summary_mcp.transcript_retriever import TranscriptRetriever, VimeoTranscriptProvider

retriever = TranscriptRetriever(provider=VimeoTranscriptProvider())
transcript = retriever.get_transcript(url)
```

### Adding a New Tool to MCP Server

1. Implement the handler method in `YouTubeSummaryServer`:

```python
async def _handle_new_tool(self, arguments: dict) -> list[types.TextContent]:
    """Handle new_tool call."""
    # Implementation
    pass
```

2. Register the tool in `_register_tools()`:

```python
Tool(
    name="new_tool",
    description="Description of the tool",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
)
```

3. Add handler in `call_tool()`:

```python
elif name == "new_tool":
    return await self._handle_new_tool(arguments)
```

## Code Style Guidelines

### Naming Conventions
- Classes: PascalCase (`TranscriptRetriever`, `SummaryGenerator`)
- Functions: snake_case (`extract_video_id`, `get_transcript`)
- Constants: UPPER_SNAKE_CASE (`DEFAULT_RATIO = 0.3`)
- Private methods: `_snake_case` (e.g., `_preprocess_text`)

### Documentation
- All public functions/classes have docstrings
- Use Google-style docstrings:

```python
def function(param1: str, param2: int) -> str:
    """
    Short description.

    Longer description if needed.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description of return value

    Raises:
        CustomError: When something goes wrong
    """
```

### Type Hints
- All functions have full type hints
- Use `Optional[T]` for nullable types
- Use `list[T]` for lists (Python 3.9+)
- Use `dict[K, V]` for dicts (Python 3.9+)

### Error Handling
- Create specific exception classes for each module
- Include context in error messages
- Log errors with appropriate level
- Use try/except to catch external API errors

## Performance Considerations

### Optimization Opportunities
1. **Caching**: Implement transcript caching
2. **Async/Await**: Use async for I/O operations
3. **Batching**: Process multiple videos in parallel
4. **Compression**: Compress cached transcripts

### Current Limitations
- Synchronous transcript fetching
- No parallel processing
- No transcript caching (optional feature)

## Future Enhancements

### Planned Features
1. Database integration for caching
2. Async/await throughout
3. More summarization algorithms (spaCy, transformers)
4. Streaming support for long videos
5. Timestamp mapping in summaries
6. Multi-language summarization
7. Sentiment analysis
8. Topic modeling

### API Considerations
1. Rate limiting implementation
2. API versioning
3. Authentication/authorization
4. Request validation

## Troubleshooting

### Common Issues

1. **youtube-transcript-api ImportError**
   ```bash
   uv pip install youtube-transcript-api
   ```

2. **nltk data not found**
   - The package auto-downloads required data
   - Manual download: `python -m nltk.downloader punkt stopwords`

3. **Import errors in tests**
   - Ensure working directory is project root
   - Run: `uv run pytest` from project root

4. **MCP connection issues**
   - Check server is running: `uv run youtube-summary-mcp`
   - Verify stdio communication
   - Check logs for errors

## Contributing

When contributing:
1. Follow SOLID principles
2. Add tests for new features
3. Update documentation
4. Run type checking: `uv run mypy youtube_summary_mcp/`
5. Format code: `uv run black youtube_summary_mcp/ tests/`
6. Lint code: `uv run ruff check youtube_summary_mcp/`

## References

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Design Patterns](https://refactoring.guru/design-patterns)
- [Type Hints](https://peps.python.org/pep-0484/)
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [NLTK Documentation](https://www.nltk.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
