"""Entry point for YouTube Summary MCP Server."""

import asyncio
import logging
import sys
from typing import Optional

from .config_manager import get_config
from .server import create_and_run_server


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
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> int:
    """
    Main entry point.

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
            "Starting %s v%s",
            config.server_name,
            config.server_version,
        )

        # Run the server
        asyncio.run(create_and_run_server())

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
    sys.exit(main())
