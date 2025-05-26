"""
Configuration loader utility for loading settings from multiple sources with override support.

This module provides functionality to load configuration from:
1. Environment variables (.env files)
2. JSON configuration files
3. Direct Python dictionary overrides

The configuration is merged with the following precedence (highest to lowest):
1. Direct overrides (passed as arguments)
2. Environment variables
3. JSON configuration files
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, TypeVar, Type
from dotenv import load_dotenv

# Type variable for generic configuration
T = TypeVar('T', bound='ConfigLoader')

class ConfigLoader:
    """Configuration loader that supports multiple configuration sources."""
    
    def __init__(self, 
                 env_path: Optional[Union[str, Path]] = None,
                 json_path: Optional[Union[str, Path]] = None,
                 env_prefix: str = "",
                 **overrides):
        """
        Initialize the configuration loader.
        
        Args:
            env_path: Path to .env file or directory containing .env
            json_path: Path to JSON configuration file
            env_prefix: Prefix for environment variables (e.g., 'APP_' for APP_SETTING)
            **overrides: Direct configuration overrides (highest precedence)
        """
        self._config: Dict[str, Any] = {}
        self.env_prefix = env_prefix
        
        # Load configuration from all sources in order of increasing precedence
        self._load_from_json(json_path)
        self._load_from_env(env_path)
        self._apply_overrides(overrides)
    
    def _load_from_env(self, env_path: Optional[Union[str, Path]] = None) -> None:
        """Load configuration from environment variables."""
        try:
            # Load .env file if path is provided
            if env_path:
                env_path = Path(env_path)
                if env_path.is_dir():
                    env_path = env_path / ".env"
                if env_path.exists():
                    load_dotenv(dotenv_path=env_path, override=True)
            
            # Load environment variables with the specified prefix
            prefix = self.env_prefix.upper()
            prefix_len = len(prefix)
            
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    # Remove prefix and convert to lowercase for the config key
                    config_key = key[prefix_len:].lower()
                    self._config[config_key] = self._parse_env_value(value)
                    
        except Exception as e:
            logging.warning(f"Failed to load environment variables: {e}")
    
    def _load_from_json(self, json_path: Optional[Union[str, Path]] = None) -> None:
        """Load configuration from a JSON file."""
        if not json_path:
            return
            
        try:
            json_path = Path(json_path)
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                    if isinstance(json_config, dict):
                        # Merge JSON config with existing config
                        self._config.update({
                            k.lower(): v for k, v in json_config.items()
                        })
        except Exception as e:
            logging.warning(f"Failed to load JSON configuration from {json_path}: {e}")
    
    def _apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Apply direct configuration overrides."""
        if overrides:
            # Convert all keys to lowercase for case-insensitive access
            lower_overrides = {k.lower(): v for k, v in overrides.items()}
            self._config.update(lower_overrides)
    
    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Parse environment variable value to appropriate Python type."""
        if not value:
            return ""
            
        # Check for boolean values
        if value.lower() in ('true', 'yes', 'on', '1'):
            return True
        if value.lower() in ('false', 'no', 'off', '0', ''):
            return False
            
        # Check for numeric values
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
            
        # Check for lists (comma-separated)
        if ',' in value:
            return [item.strip() for item in value.split(',')]
            
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        return self._config.get(key.lower(), default)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', 'yes', 'on', '1')
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        try:
            return int(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        try:
            return float(self.get(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """Get a list configuration value."""
        if default is None:
            default = []
            
        value = self.get(key)
        if value is None:
            return default
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return [value]
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the configuration as a dictionary."""
        return self._config.copy()
    
    @classmethod
    def from_dict(cls: Type[T], config_dict: Dict[str, Any], **overrides) -> T:
        """Create a ConfigLoader instance from a dictionary."""
        instance = cls(**overrides)
        instance._config.update({k.lower(): v for k, v in config_dict.items()})
        if overrides:
            instance._apply_overrides(overrides)
        return instance


def load_config(
    env_path: Optional[Union[str, Path]] = None,
    json_path: Optional[Union[str, Path]] = None,
    env_prefix: str = "",
    **overrides
) -> ConfigLoader:
    """
    Load configuration from multiple sources with override support.
    
    Args:
        env_path: Path to .env file or directory containing .env
        json_path: Path to JSON configuration file
        env_prefix: Prefix for environment variables
        **overrides: Direct configuration overrides (highest precedence)
        
    Returns:
        ConfigLoader instance with loaded configuration
    """
    return ConfigLoader(
        env_path=env_path,
        json_path=json_path,
        env_prefix=env_prefix,
        **overrides
    )
