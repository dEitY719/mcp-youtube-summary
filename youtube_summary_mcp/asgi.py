"""ASGI application for YouTube Summary MCP Server with SSE transport.

This module can be used with Uvicorn or other ASGI servers:

    # With default settings
    uvicorn youtube_summary_mcp.asgi:app --host 0.0.0.0 --port 10719

    # With custom settings
    MCP_SSE_HOST=127.0.0.1 MCP_SSE_PORT=8080 uvicorn youtube_summary_mcp.asgi:app
"""

import logging
from .server_sse import create_server_sse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create the FastMCP server instance (ASGI app)
app = create_server_sse()

logger.info("ASGI app initialized for SSE transport")
