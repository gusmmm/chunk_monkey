"""
Config Package for Chunk Monkey
===============================

This package contains configuration management modules for the Chunk Monkey pipeline.
It handles application settings, environment variables, feature flags, and
configuration validation.

Modules:
- settings: Main configuration settings and validation
- environment: Environment variable handling
- defaults: Default configuration values
- validation: Configuration validation utilities

Author: Chunk Monkey Team
"""

from .settings import (
    get_config,
    validate_config,
    load_env_config,
    PDFProcessingConfig,
    JSONConfig,
    HTMLConfig,
    MarkdownConfig,
    LoggingConfig,
    PerformanceConfig,
    FeatureFlags,
    DEFAULT_OUTPUT_DIR,
    TEMPLATES_DIR,
    FILE_NAMING,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS
)

__all__ = [
    'get_config',
    'validate_config',
    'load_env_config',
    'PDFProcessingConfig',
    'JSONConfig',
    'HTMLConfig',
    'MarkdownConfig',
    'LoggingConfig',
    'PerformanceConfig',
    'FeatureFlags',
    'DEFAULT_OUTPUT_DIR',
    'TEMPLATES_DIR',
    'FILE_NAMING',
    'SUPPORTED_INPUT_FORMATS',
    'SUPPORTED_OUTPUT_FORMATS'
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Configuration management for Chunk Monkey pipeline"

# Configuration validation on import
def _validate_on_import():
    """Validate configuration when package is imported."""
    try:
        config = get_config()
        is_valid = validate_config()
        if not is_valid:
            import warnings
            warnings.warn(
                "Configuration validation failed. Some features may not work correctly.",
                UserWarning
            )
    except Exception:
        # Silent fail on import - validation can be called explicitly
        pass

# Run validation
_validate_on_import()
