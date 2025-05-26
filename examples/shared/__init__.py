"""
Shared utilities for Taskinity DSL examples.

This package contains common functionality used across different example projects,
such as configuration loading, logging, OCR processing, and other utilities.
"""

from .utils.config_loader import ConfigLoader, load_config
from .utils.local_ocr import LocalOCRProcessor, create_ocr_processor

__all__ = [
    'ConfigLoader', 
    'load_config',
    'LocalOCRProcessor',
    'create_ocr_processor'
]
