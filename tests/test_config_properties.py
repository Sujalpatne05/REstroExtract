"""
Property-based tests for ConfigManager.

Feature: fssai-restaurant-scraper
Property 16: Configuration Management Correctness

**Validates: Requirements 9.1, 9.2, 9.3**

For any configuration provided (file, CLI arguments, or environment variables),
the scraper must validate all configuration values, use defaults for missing values,
and apply CLI arguments with highest priority before beginning execution.
"""

import os
import json
import tempfile
from hypothesis import given, strategies as st, settings
from src.config import ConfigManager


# Custom strategies for generating valid configuration values
@st.composite
def valid_log_levels(draw):
    """Generate valid log level values."""
    return draw(st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]))


@st.composite
def valid_states(draw):
    """Generate valid state values."""
    return draw(st.sampled_from(["Maharashtra", "All"]))


@st.composite
def positive_integers(draw):
    """Generate positive integers."""
    return draw(st.integers(min_value=1, max_value=1000))


@st.composite
def positive_floats(draw):
    """Generate positive floats."""
    return draw(st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False))


@st.composite
def valid_cli_args(draw):
    """Generate valid CLI arguments."""
    return {
        "state": draw(st.one_of(st.none(), valid_states())),
        "timeout": draw(st.one_of(st.none(), positive_integers())),
        "rate_limit": draw(st.one_of(st.none(), positive_floats())),
        "max_retries": draw(st.one_of(st.none(), positive_integers())),
        "log_level": draw(st.one_of(st.none(), valid_log_levels())),
    }


class TestConfigurationManagementCorrectness:
    """
    Property 16: Configuration Management Correctness
    
    For any configuration provided (file, CLI arguments, or environment variables),
    the scraper must validate all configuration values, use defaults for missing values,
    and apply CLI arguments with highest priority before beginning execution.
    """
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_cli_args_highest_priority(self, cli_args):
        """
        Property: CLI arguments have highest priority over all other sources.
        
        For any CLI arguments provided, they must override defaults and be
        reflected in the final configuration.
        """
        config = ConfigManager(cli_args=cli_args)
        
        # Verify CLI arguments are applied
        if cli_args.get("state") is not None:
            assert config.get("target_state") == cli_args["state"]
        
        if cli_args.get("timeout") is not None:
            assert config.get("request_timeout") == cli_args["timeout"]
        
        if cli_args.get("rate_limit") is not None:
            assert config.get("rate_limit_delay") == cli_args["rate_limit"]
        
        if cli_args.get("max_retries") is not None:
            assert config.get("max_retries") == cli_args["max_retries"]
        
        if cli_args.get("log_level") is not None:
            assert config.get("log_level") == cli_args["log_level"]
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_defaults_used_for_missing_values(self, cli_args):
        """
        Property: Default values are used for missing configuration values.
        
        For any missing CLI arguments, the configuration must use default values
        instead of leaving them undefined.
        """
        config = ConfigManager(cli_args=cli_args)
        
        # Verify all keys exist in configuration
        assert "target_state" in config.get_all()
        assert "output_directory" in config.get_all()
        assert "request_timeout" in config.get_all()
        assert "rate_limit_delay" in config.get_all()
        assert "max_retries" in config.get_all()
        assert "log_level" in config.get_all()
        assert "log_file" in config.get_all()
        
        # Verify defaults are used when CLI args are None
        if cli_args.get("state") is None:
            assert config.get("target_state") == "Maharashtra"
        
        if cli_args.get("timeout") is None:
            assert config.get("request_timeout") == 30
        
        if cli_args.get("rate_limit") is None:
            assert config.get("rate_limit_delay") == 1.0
        
        if cli_args.get("max_retries") is None:
            assert config.get("max_retries") == 3
        
        if cli_args.get("log_level") is None:
            assert config.get("log_level") == "INFO"
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_configuration_validation_passes(self, cli_args):
        """
        Property: All valid configuration values pass validation.
        
        For any valid CLI arguments, the configuration must pass validation
        without raising exceptions.
        """
        # This should not raise any exceptions
        config = ConfigManager(cli_args=cli_args)
        
        # Verify configuration is valid
        assert config.validate_config() is True
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_get_method_returns_configured_values(self, cli_args):
        """
        Property: The get() method returns configured values correctly.
        
        For any configuration, the get() method must return the correct value
        for any key that exists in the configuration.
        """
        config = ConfigManager(cli_args=cli_args)
        
        # Verify get() returns correct values
        assert config.get("target_state") is not None
        assert config.get("output_directory") is not None
        assert config.get("request_timeout") is not None
        assert config.get("rate_limit_delay") is not None
        assert config.get("max_retries") is not None
        assert config.get("log_level") is not None
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_get_all_returns_complete_configuration(self, cli_args):
        """
        Property: The get_all() method returns all configuration values.
        
        For any configuration, get_all() must return a dictionary containing
        all required configuration keys.
        """
        config = ConfigManager(cli_args=cli_args)
        all_config = config.get_all()
        
        # Verify all required keys are present
        required_keys = [
            "target_state",
            "output_directory",
            "request_timeout",
            "rate_limit_delay",
            "max_retries",
            "log_level",
            "log_file"
        ]
        
        for key in required_keys:
            assert key in all_config
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_configuration_types_are_correct(self, cli_args):
        """
        Property: Configuration values have correct types.
        
        For any configuration, all values must have the correct type:
        - target_state: str
        - output_directory: str
        - request_timeout: int
        - rate_limit_delay: float
        - max_retries: int
        - log_level: str
        - log_file: str
        """
        config = ConfigManager(cli_args=cli_args)
        
        assert isinstance(config.get("target_state"), str)
        assert isinstance(config.get("output_directory"), str)
        assert isinstance(config.get("request_timeout"), int)
        assert isinstance(config.get("rate_limit_delay"), (int, float))
        assert isinstance(config.get("max_retries"), int)
        assert isinstance(config.get("log_level"), str)
        assert isinstance(config.get("log_file"), str)
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_configuration_values_are_valid(self, cli_args):
        """
        Property: Configuration values are within valid ranges.
        
        For any configuration, all values must be within valid ranges:
        - request_timeout > 0
        - rate_limit_delay > 0
        - max_retries >= 0
        - log_level in VALID_LOG_LEVELS
        - target_state in VALID_STATES
        """
        config = ConfigManager(cli_args=cli_args)
        
        assert config.get("request_timeout") > 0
        assert config.get("rate_limit_delay") > 0
        assert config.get("max_retries") >= 0
        assert config.get("log_level") in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert config.get("target_state") in ["Maharashtra", "All"]
    
    @given(cli_args=valid_cli_args())
    @settings(max_examples=100)
    def test_load_config_idempotent(self, cli_args):
        """
        Property: Calling load_config() multiple times produces same result.
        
        For any configuration, calling load_config() multiple times must
        produce the same configuration values.
        """
        config = ConfigManager(cli_args=cli_args)
        first_load = config.get_all()
        
        # Call load_config again
        second_load = config.load_config()
        
        # Both should be identical
        assert first_load == second_load
