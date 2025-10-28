"""Configuration management for YouTube Summary MCP Server."""

import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


logger = logging.getLogger(__name__)


class ConfigManager(BaseSettings):
    """
    Configuration manager for YouTube Summary MCP Server.

    Handles configuration from environment variables and .env files.
    Follows Single Responsibility Principle by managing only configuration.
    """

    # API Configuration
    youtube_api_key: Optional[str] = Field(
        default=None,
        description="YouTube API key (optional, uses youtube-transcript-api by default)",
    )

    # Summary Configuration
    summary_length: str = Field(
        default="medium",
        description="Default summary length: short, medium, or long",
    )
    summary_ratio: float = Field(
        default=0.3,
        description="Ratio of summary to original text (0.0 to 1.0)",
    )

    # Language Configuration
    default_language: str = Field(
        default="en",
        description="Default language for transcripts",
    )
    supported_languages: list[str] = Field(
        default=["en", "ko", "es", "fr", "de", "ja", "zh"],
        description="List of supported languages",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting",
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Number of requests allowed per rate limit window",
    )
    rate_limit_window_seconds: int = Field(
        default=3600,
        description="Rate limit window in seconds",
    )

    # Caching
    cache_enabled: bool = Field(
        default=True,
        description="Enable caching of transcripts",
    )
    cache_ttl_seconds: int = Field(
        default=86400,
        description="Cache time-to-live in seconds (default: 24 hours)",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    # Server Configuration
    server_name: str = Field(
        default="YouTube Summary MCP",
        description="Name of the MCP server",
    )
    server_version: str = Field(
        default="0.1.0",
        description="Version of the MCP server",
    )

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("summary_length")
    @classmethod
    def validate_summary_length(cls, v: str) -> str:
        """Validate summary length value."""
        valid_lengths = ["short", "medium", "long"]
        if v.lower() not in valid_lengths:
            raise ValueError(
                f"summary_length must be one of {valid_lengths}, got {v}"
            )
        return v.lower()

    @field_validator("summary_ratio")
    @classmethod
    def validate_summary_ratio(cls, v: float) -> float:
        """Validate summary ratio value."""
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"summary_ratio must be between 0.0 and 1.0, got {v}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(
                f"log_level must be one of {valid_levels}, got {v}"
            )
        return v.upper()

    def get_summary_length_ratio(self) -> float:
        """
        Get summary ratio based on summary length setting.

        Returns:
            float: Summary ratio (0.0 to 1.0)
        """
        length_ratios = {
            "short": 0.2,
            "medium": 0.35,
            "long": 0.5,
        }
        return length_ratios.get(self.summary_length, self.summary_ratio)

    def setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.info(
            f"Logging configured with level: {self.log_level}"
        )


# Global configuration instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get the global configuration instance.

    Creates a new instance if none exists (Singleton pattern).

    Returns:
        ConfigManager: Global configuration instance
    """
    global _config
    if _config is None:
        _config = ConfigManager()
        _config.setup_logging()
    return _config


def set_config(config: ConfigManager) -> None:
    """
    Set the global configuration instance.

    Useful for testing.

    Args:
        config: ConfigManager instance to set as global
    """
    global _config
    _config = config
