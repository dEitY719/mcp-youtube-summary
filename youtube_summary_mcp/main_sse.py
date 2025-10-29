"""Entry point for YouTube Summary MCP Server using FastMCP with SSE transport."""

import logging
import sys
from typing import Optional

from .config_manager import get_config
from .server_sse import create_server_sse


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (optional)
    """
    config = get_config()
    effective_level = log_level or config.log_level

    logging.basicConfig(
        level=getattr(logging, effective_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
        ],
    )


def main_sse() -> int:
    """
    Main entry point for SSE transport.

    Reads configuration from environment variables:
    - MCP_SSE_HOST: Host to bind to (default: 0.0.0.0)
    - MCP_SSE_PORT: Port to bind to (default: 10719)
    - MCP_SSE_PATH: SSE endpoint path (default: /sse)

    Returns:
        Exit code
    """
    # Set up logging first
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Get configuration
        config = get_config()
        logger.info(
            "Starting %s v%s (SSE transport)",
            config.server_name,
            config.server_version,
        )

        # Create and run the FastMCP server with SSE transport
        server = create_server_sse()
        server.run(transport="sse")

        return 0

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        return 0

    except OSError as e:
        logger.error("OS error: %s", str(e), exc_info=True)
        return 1

    except Exception as e:  # pylint: disable=broad-except
        logger.error("Fatal error: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main_sse())
