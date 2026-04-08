"""
Unit tests for ConfigManager class.

Tests configuration loading from multiple sources with proper priority:
- CLI arguments (highest priority)
- Configuration file (YAML/JSON)
- Environment variables
- Default values (lowest priority)
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from src.config import ConfigManager


class TestConfigManagerDefaults:
    """Test default configuration values."""
    
    def test_default_values_loaded(self):
        """Test that default values are loaded when no config provided."""
        config = ConfigManager()
        
        assert config.get("target_state") == "Maharashtra"
        assert config.get("output_directory") == "./output"
        assert config.get("request_timeout") == 30
        assert config.get("rate_limit_delay") == 1.0
        assert config.get("max_retries") == 3
        assert config.get("log_level") == "INFO"
    
    def test_get_all_returns_all_config(self):
        """Test that get_all() returns all configuration values."""
        config = ConfigManager()
        all_config = config.get_all()
        
        assert "target_state" in all_config
        assert "output_directory" in all_config
        assert "request_timeout" in all_config
        assert "rate_limit_delay" in all_config
        assert "max_retries" in all_config
        assert "log_level" in all_config
        assert "log_file" in all_config
    
    def test_get_with_default(self):
        """Test get() method with default value."""
        config = ConfigManager()
        
        # Non-existent key should return default
        assert config.get("nonexistent", "default_value") == "default_value"


class TestConfigManagerJSON:
    """Test loading configuration from JSON files."""
    
    def test_load_json_config(self):
        """Test loading configuration from JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "target_state": "All",
                "request_timeout": 60,
                "max_retries": 5
            }, f)
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            
            assert config.get("target_state") == "All"
            assert config.get("request_timeout") == 60
            assert config.get("max_retries") == 5
            # Other values should be defaults
            assert config.get("rate_limit_delay") == 1.0
        finally:
            os.unlink(config_file)
    
    def test_json_config_file_not_found(self):
        """Test error when JSON config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            ConfigManager(config_file="/nonexistent/config.json")
    
    def test_invalid_json_file(self):
        """Test error when JSON file is invalid."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name
        
        try:
            with pytest.raises(ValueError):
                ConfigManager(config_file=config_file)
        finally:
            os.unlink(config_file)


class TestConfigManagerYAML:
    """Test loading configuration from YAML files."""
    
    def test_load_yaml_config(self):
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("target_state: All\n")
            f.write("request_timeout: 60\n")
            f.write("max_retries: 5\n")
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            
            assert config.get("target_state") == "All"
            assert config.get("request_timeout") == 60
            assert config.get("max_retries") == 5
        finally:
            os.unlink(config_file)
    
    def test_load_yml_config(self):
        """Test loading configuration from .yml file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("target_state: Maharashtra\n")
            f.write("rate_limit_delay: 2.5\n")
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            
            assert config.get("target_state") == "Maharashtra"
            assert config.get("rate_limit_delay") == 2.5
        finally:
            os.unlink(config_file)


class TestConfigManagerEnvironmentVariables:
    """Test loading configuration from environment variables."""
    
    def test_load_from_env_variables(self):
        """Test loading configuration from environment variables."""
        os.environ["FSSAI_TARGET_STATE"] = "All"
        os.environ["FSSAI_REQUEST_TIMEOUT"] = "45"
        os.environ["FSSAI_RATE_LIMIT"] = "2.5"
        
        try:
            config = ConfigManager()
            
            assert config.get("target_state") == "All"
            assert config.get("request_timeout") == 45
            assert config.get("rate_limit_delay") == 2.5
        finally:
            del os.environ["FSSAI_TARGET_STATE"]
            del os.environ["FSSAI_REQUEST_TIMEOUT"]
            del os.environ["FSSAI_RATE_LIMIT"]
    
    def test_env_variables_override_defaults(self):
        """Test that environment variables override defaults."""
        os.environ["FSSAI_LOG_LEVEL"] = "DEBUG"
        
        try:
            config = ConfigManager()
            assert config.get("log_level") == "DEBUG"
        finally:
            del os.environ["FSSAI_LOG_LEVEL"]


class TestConfigManagerCLIArguments:
    """Test loading configuration from CLI arguments."""
    
    def test_cli_args_override_all(self):
        """Test that CLI arguments override all other sources."""
        # Set environment variable
        os.environ["FSSAI_TARGET_STATE"] = "All"
        
        # Create config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"target_state": "Maharashtra"}, f)
            config_file = f.name
        
        try:
            # CLI args should override both env and file
            cli_args = {"state": "All"}
            config = ConfigManager(config_file=config_file, cli_args=cli_args)
            
            assert config.get("target_state") == "All"
        finally:
            os.unlink(config_file)
            if "FSSAI_TARGET_STATE" in os.environ:
                del os.environ["FSSAI_TARGET_STATE"]
    
    def test_cli_args_with_numeric_values(self):
        """Test CLI arguments with numeric values."""
        cli_args = {
            "timeout": 60,
            "rate_limit": 2.5,
            "max_retries": 5
        }
        config = ConfigManager(cli_args=cli_args)
        
        assert config.get("request_timeout") == 60
        assert config.get("rate_limit_delay") == 2.5
        assert config.get("max_retries") == 5
    
    def test_cli_args_with_string_numeric_values(self):
        """Test CLI arguments with string numeric values."""
        cli_args = {
            "timeout": "60",
            "rate_limit": "2.5",
            "max_retries": "5"
        }
        config = ConfigManager(cli_args=cli_args)
        
        assert config.get("request_timeout") == 60
        assert config.get("rate_limit_delay") == 2.5
        assert config.get("max_retries") == 5


class TestConfigManagerPriority:
    """Test configuration priority (CLI > file > env > defaults)."""
    
    def test_priority_cli_over_file(self):
        """Test that CLI arguments override config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"request_timeout": 30}, f)
            config_file = f.name
        
        try:
            cli_args = {"timeout": 60}
            config = ConfigManager(config_file=config_file, cli_args=cli_args)
            
            assert config.get("request_timeout") == 60
        finally:
            os.unlink(config_file)
    
    def test_priority_file_over_env(self):
        """Test that config file overrides environment variables."""
        os.environ["FSSAI_REQUEST_TIMEOUT"] = "45"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"request_timeout": 60}, f)
            config_file = f.name
        
        try:
            config = ConfigManager(config_file=config_file)
            assert config.get("request_timeout") == 60
        finally:
            os.unlink(config_file)
            del os.environ["FSSAI_REQUEST_TIMEOUT"]
    
    def test_priority_env_over_defaults(self):
        """Test that environment variables override defaults."""
        os.environ["FSSAI_MAX_RETRIES"] = "10"
        
        try:
            config = ConfigManager()
            assert config.get("max_retries") == 10
        finally:
            del os.environ["FSSAI_MAX_RETRIES"]


class TestConfigManagerValidation:
    """Test configuration validation."""
    
    def test_validate_request_timeout_positive(self):
        """Test that request_timeout must be positive."""
        cli_args = {"timeout": -1}
        
        with pytest.raises(ValueError, match="request_timeout must be positive"):
            ConfigManager(cli_args=cli_args)
    
    def test_validate_rate_limit_positive(self):
        """Test that rate_limit_delay must be positive."""
        cli_args = {"rate_limit": 0}
        
        with pytest.raises(ValueError, match="rate_limit_delay must be positive"):
            ConfigManager(cli_args=cli_args)
    
    def test_validate_max_retries_non_negative(self):
        """Test that max_retries must be non-negative."""
        cli_args = {"max_retries": -1}
        
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            ConfigManager(cli_args=cli_args)
    
    def test_validate_log_level_valid(self):
        """Test that log_level must be valid."""
        cli_args = {"log_level": "INVALID"}
        
        with pytest.raises(ValueError, match="log_level must be one of"):
            ConfigManager(cli_args=cli_args)
    
    def test_validate_target_state_valid(self):
        """Test that target_state must be valid."""
        cli_args = {"state": "InvalidState"}
        
        with pytest.raises(ValueError, match="target_state must be one of"):
            ConfigManager(cli_args=cli_args)
    
    def test_validate_output_directory_created(self):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = os.path.join(tmpdir, "new_output")
            cli_args = {"output": output_dir}
            
            config = ConfigManager(cli_args=cli_args)
            
            assert os.path.exists(output_dir)
            assert config.get("output_directory") == output_dir
    
    def test_validate_log_directory_created(self):
        """Test that log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "logs", "scraper.log")
            cli_args = {"log_file": log_file}
            
            config = ConfigManager(cli_args=cli_args)
            
            log_dir = os.path.dirname(log_file)
            assert os.path.exists(log_dir)


class TestConfigManagerIntegration:
    """Integration tests for ConfigManager."""
    
    def test_full_priority_chain(self):
        """Test full priority chain: CLI > file > env > defaults."""
        # Set environment variable
        os.environ["FSSAI_TARGET_STATE"] = "All"
        os.environ["FSSAI_REQUEST_TIMEOUT"] = "45"
        
        # Create config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({
                "target_state": "Maharashtra",
                "request_timeout": 60,
                "max_retries": 5
            }, f)
            config_file = f.name
        
        try:
            # CLI args override everything
            cli_args = {"state": "All"}
            config = ConfigManager(config_file=config_file, cli_args=cli_args)
            
            # CLI overrides file and env
            assert config.get("target_state") == "All"
            # File overrides env
            assert config.get("request_timeout") == 60
            # File value used
            assert config.get("max_retries") == 5
        finally:
            os.unlink(config_file)
            del os.environ["FSSAI_TARGET_STATE"]
            del os.environ["FSSAI_REQUEST_TIMEOUT"]
    
    def test_load_config_returns_dict(self):
        """Test that load_config() returns a dictionary."""
        config = ConfigManager()
        result = config.load_config()
        
        assert isinstance(result, dict)
        assert "target_state" in result
        assert "output_directory" in result
