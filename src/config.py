"""
Configuration Management Module

Handles loading and validation of configuration from multiple sources:
- Command-line arguments (highest priority)
- Configuration files (YAML/JSON)
- Environment variables
- Default values (lowest priority)
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path


class ConfigManager:
    """
    Manages configuration loading and validation from multiple sources.
    
    Configuration priority (highest to lowest):
    1. CLI arguments
    2. Configuration file (YAML/JSON)
    3. Environment variables
    4. Default values
    """
    
    # Default configuration values
    DEFAULTS = {
        "target_state": "Maharashtra",
        "output_directory": "./output",
        "request_timeout": 30,
        "rate_limit_delay": 1.0,
        "max_retries": 3,
        "log_file": "./logs/scraper.log",
        "log_level": "INFO",
    }
    
    # Valid values for certain configuration options
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    VALID_STATES = ["Maharashtra", "All"]
    
    def __init__(self, config_file: Optional[str] = None, cli_args: Optional[Dict] = None):
        """
        Initialize ConfigManager.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
            cli_args: Dictionary of CLI arguments
        """
        self.config_file = config_file
        self.cli_args = cli_args or {}
        self.config = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from all sources with proper priority.
        
        Returns:
            Dictionary containing merged configuration
        """
        # Start with defaults
        self.config = self.DEFAULTS.copy()
        
        # Load from environment variables
        self._load_from_env()
        
        # Load from configuration file
        if self.config_file:
            self._load_from_file()
        
        # Override with CLI arguments (highest priority)
        self._load_from_cli()
        
        # Validate configuration
        self.validate_config()
        
        return self.config
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mapping = {
            "FSSAI_TARGET_STATE": "target_state",
            "FSSAI_OUTPUT_DIR": "output_directory",
            "FSSAI_REQUEST_TIMEOUT": "request_timeout",
            "FSSAI_RATE_LIMIT": "rate_limit_delay",
            "FSSAI_MAX_RETRIES": "max_retries",
            "FSSAI_LOG_FILE": "log_file",
            "FSSAI_LOG_LEVEL": "log_level",
        }
        
        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert to appropriate type
                if config_key in ["request_timeout", "max_retries"]:
                    try:
                        self.config[config_key] = int(value)
                    except ValueError:
                        pass
                elif config_key == "rate_limit_delay":
                    try:
                        self.config[config_key] = float(value)
                    except ValueError:
                        pass
                else:
                    self.config[config_key] = value
    
    def _load_from_file(self) -> None:
        """Load configuration from YAML or JSON file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        file_ext = Path(self.config_file).suffix.lower()
        
        try:
            if file_ext == ".json":
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            elif file_ext in [".yaml", ".yml"]:
                # Try to import yaml, fall back to simple parsing if not available
                try:
                    import yaml
                    with open(self.config_file, "r") as f:
                        file_config = yaml.safe_load(f)
                        if file_config:
                            self.config.update(file_config)
                except ImportError:
                    # Simple YAML parsing for basic key: value format
                    with open(self.config_file, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                if ":" in line:
                                    key, value = line.split(":", 1)
                                    key = key.strip()
                                    value = value.strip()
                                    
                                    # Convert to appropriate type
                                    if key in ["request_timeout", "max_retries"]:
                                        try:
                                            self.config[key] = int(value)
                                        except ValueError:
                                            self.config[key] = value
                                    elif key == "rate_limit_delay":
                                        try:
                                            self.config[key] = float(value)
                                        except ValueError:
                                            self.config[key] = value
                                    else:
                                        self.config[key] = value
            else:
                raise ValueError(f"Unsupported config file format: {file_ext}")
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Error parsing configuration file: {e}")
    
    def _load_from_cli(self) -> None:
        """Load configuration from CLI arguments."""
        cli_mapping = {
            "state": "target_state",
            "output": "output_directory",
            "timeout": "request_timeout",
            "rate_limit": "rate_limit_delay",
            "max_retries": "max_retries",
            "log_file": "log_file",
            "log_level": "log_level",
            "append_mode": "append_mode",
            "use_mock_data": "use_mock_data",
        }
        
        for cli_key, config_key in cli_mapping.items():
            if cli_key in self.cli_args and self.cli_args[cli_key] is not None:
                value = self.cli_args[cli_key]
                
                # Convert to appropriate type
                if config_key in ["request_timeout", "max_retries"]:
                    try:
                        self.config[config_key] = int(value)
                    except (ValueError, TypeError):
                        self.config[config_key] = value
                elif config_key == "rate_limit_delay":
                    try:
                        self.config[config_key] = float(value)
                    except (ValueError, TypeError):
                        self.config[config_key] = value
                elif config_key in ["append_mode", "use_mock_data"]:
                    # Handle boolean flags
                    self.config[config_key] = bool(value)
                else:
                    self.config[config_key] = value
    
    def validate_config(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate request timeout
        if not isinstance(self.config["request_timeout"], (int, float)):
            raise ValueError("request_timeout must be a number")
        if self.config["request_timeout"] <= 0:
            raise ValueError("request_timeout must be positive")
        
        # Validate rate limit delay
        if not isinstance(self.config["rate_limit_delay"], (int, float)):
            raise ValueError("rate_limit_delay must be a number")
        if self.config["rate_limit_delay"] <= 0:
            raise ValueError("rate_limit_delay must be positive")
        
        # Validate max retries
        if not isinstance(self.config["max_retries"], int):
            raise ValueError("max_retries must be an integer")
        if self.config["max_retries"] < 0:
            raise ValueError("max_retries must be non-negative")
        
        # Validate log level
        if self.config["log_level"] not in self.VALID_LOG_LEVELS:
            raise ValueError(f"log_level must be one of {self.VALID_LOG_LEVELS}")
        
        # Validate target state
        if self.config["target_state"] not in self.VALID_STATES:
            raise ValueError(f"target_state must be one of {self.VALID_STATES}")
        
        # Validate output directory exists or can be created
        output_dir = self.config["output_directory"]
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create output directory: {e}")
        
        # Validate log directory exists or can be created
        log_file = self.config["log_file"]
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create log directory: {e}")
        
        return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary containing all configuration
        """
        return self.config.copy()
