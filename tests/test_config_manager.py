"""Tests for config_manager module."""

import pytest

from youtube_summary_mcp.config_manager import (
    ConfigManager,
    get_config,
    set_config,
)


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_config_manager_initialization(self) -> None:
        """Test ConfigManager initialization."""
        config = ConfigManager()
        assert config is not None
        assert config.server_name == "YouTube Summary MCP"
        assert config.summary_length == "medium"

    def test_config_manager_summary_length_validation(self) -> None:
        """Test summary_length validation."""
        config = ConfigManager(summary_length="short")
        assert config.summary_length == "short"

        with pytest.raises(ValueError):
            ConfigManager(summary_length="invalid")

    def test_config_manager_summary_ratio_validation(self) -> None:
        """Test summary_ratio validation."""
        config = ConfigManager(summary_ratio=0.5)
        assert config.summary_ratio == 0.5

        with pytest.raises(ValueError):
            ConfigManager(summary_ratio=1.5)

        with pytest.raises(ValueError):
            ConfigManager(summary_ratio=-0.1)

    def test_config_manager_log_level_validation(self) -> None:
        """Test log_level validation."""
        config = ConfigManager(log_level="DEBUG")
        assert config.log_level == "DEBUG"

        with pytest.raises(ValueError):
            ConfigManager(log_level="INVALID")

    def test_get_summary_length_ratio(self) -> None:
        """Test get_summary_length_ratio method."""
        config = ConfigManager()

        config.summary_length = "short"
        assert config.get_summary_length_ratio() == 0.2

        config.summary_length = "medium"
        assert config.get_summary_length_ratio() == 0.35

        config.summary_length = "long"
        assert config.get_summary_length_ratio() == 0.5

    def test_get_config_singleton(self) -> None:
        """Test get_config singleton behavior."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_set_config(self) -> None:
        """Test set_config function."""
        new_config = ConfigManager(server_name="Test Server")
        set_config(new_config)

        retrieved_config = get_config()
        assert retrieved_config.server_name == "Test Server"

        # Reset to default
        set_config(ConfigManager())
