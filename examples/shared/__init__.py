"""
Shared utilities for Taskinity DSL examples.

This package contains common functionality used across different example projects,
such as configuration loading, logging, and other utilities.
"""

from .utils.config_loader import ConfigLoader, load_config

__all__ = ['ConfigLoader', 'load_config']
