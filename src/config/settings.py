"""
Configuration settings for Chunk Monkey PDF processing pipeline.

This module contains all configurable parameters for the application,
including processing options, output settings, and feature flags.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# PDF Processing Configuration
class PDFProcessingConfig:
    """Configuration for PDF processing with Docling."""

    # Image processing settings
    IMAGE_SCALE: float = 2.0  # Scale factor for extracted images (1.0 = 72 DPI)
    GENERATE_PAGE_IMAGES: bool = True  # Generate full page images
    GENERATE_PICTURE_IMAGES: bool = True  # Extract individual pictures
    GENERATE_TABLE_IMAGES: bool = True  # Generate table images

    # Text extraction settings
    PRESERVE_WHITESPACE: bool = True
    EXTRACT_FONTS: bool = True
    EXTRACT_METADATA: bool = True

    # Section detection settings
    MAIN_HEADER_MIN_LENGTH: int = 40  # Minimum length for main headers
    DETECT_REFERENCES: bool = True
    REFERENCE_KEYWORDS: List[str] = [
        "references", "bibliography", "citations", "works cited"
    ]

    # Quality settings
    OCR_ENABLED: bool = True
    TABLE_EXTRACTION_METHOD: str = "hybrid"  # "hybrid", "rule_based", "ml"

# JSON Structure Configuration
class JSONConfig:
    """Configuration for JSON output structure."""

    INCLUDE_METADATA: bool = True
    INCLUDE_TIMESTAMPS: bool = True
    INCLUDE_SECTION_HIERARCHY: bool = True
    INCLUDE_POSITION_INFO: bool = True

    # Content filtering
    MIN_TEXT_LENGTH: int = 10  # Minimum text length to include
    FILTER_EMPTY_SECTIONS: bool = True
    MERGE_ADJACENT_TEXT: bool = False

    # Encoding settings
    ENSURE_ASCII: bool = False
    INDENT_SIZE: int = 4

# HTML Generation Configuration
class HTMLConfig:
    """Configuration for HTML output generation."""

    # Template settings
    DEFAULT_TEMPLATE: str = "document.html"
    THEME: str = "modern"  # "modern", "classic", "minimal"

    # Layout settings
    RESPONSIVE_DESIGN: bool = True
    INCLUDE_TOC: bool = True  # Table of Contents
    INCLUDE_STATS: bool = True  # Document statistics
    ENABLE_SEARCH: bool = True

    # Content display
    IMAGES_INLINE: bool = True
    TABLES_COLLAPSIBLE: bool = True
    CODE_HIGHLIGHTING: bool = True

    # Performance settings
    LAZY_LOAD_IMAGES: bool = True
    MINIFY_HTML: bool = False
    INCLUDE_SOURCE_MAPS: bool = False

# Markdown Configuration
class MarkdownConfig:
    """Configuration for Markdown processing and output."""

    # Parsing settings
    PRESERVE_TABLES: bool = True
    PRESERVE_IMAGES: bool = True
    PRESERVE_LINKS: bool = True

    # Output formatting
    HEADER_STYLE: str = "atx"  # "atx" (#) or "setext" (underline)
    LIST_INDENT: int = 2
    CODE_FENCE_STYLE: str = "```"  # "```" or "~~~"

    # Content processing
    AUTO_LINK_URLS: bool = True
    ESCAPE_HTML: bool = True
    SMART_QUOTES: bool = True

# Logging Configuration
class LoggingConfig:
    """Configuration for application logging."""

    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_TO_FILE: bool = True
    LOG_FILE: str = "chunk_monkey.log"

    # Console output
    RICH_CONSOLE: bool = True  # Use rich for colored console output
    SHOW_PROGRESS: bool = True  # Show progress bars
    VERBOSE_ERRORS: bool = True  # Show detailed error messages

# Performance Configuration
class PerformanceConfig:
    """Configuration for performance optimization."""

    # Memory management
    MAX_MEMORY_MB: int = 2048  # Maximum memory usage in MB
    CLEANUP_TEMP_FILES: bool = True
    CACHE_ENABLED: bool = True
    CACHE_DIR: str = ".cache"

    # Processing limits
    MAX_FILE_SIZE_MB: int = 100  # Maximum PDF file size
    MAX_PAGES: Optional[int] = None  # Maximum pages to process (None = unlimited)
    PARALLEL_PROCESSING: bool = True
    MAX_WORKERS: int = 4  # Number of parallel workers

# Feature Flags
class FeatureFlags:
    """Feature flags for enabling/disabling functionality."""

    # Core features
    ENABLE_PDF_PROCESSING: bool = True
    ENABLE_MARKDOWN_PARSING: bool = True
    ENABLE_JSON_EXPORT: bool = True
    ENABLE_HTML_GENERATION: bool = True

    # Advanced features
    ENABLE_SECTION_FILTERING: bool = True
    ENABLE_BATCH_PROCESSING: bool = True
    ENABLE_LLM_INTEGRATION: bool = False
    ENABLE_CLOUD_STORAGE: bool = False

    # Experimental features
    ENABLE_OCR_FALLBACK: bool = False
    ENABLE_AI_SUMMARIZATION: bool = False
    ENABLE_SEMANTIC_CHUNKING: bool = False

# File Extensions and MIME Types
SUPPORTED_INPUT_FORMATS = {
    ".pdf": "application/pdf",
    ".md": "text/markdown",
    ".txt": "text/plain"
}

SUPPORTED_OUTPUT_FORMATS = {
    "json": ".json",
    "html": ".html",
    "md": ".md",
    "txt": ".txt"
}

# Default file naming patterns
FILE_NAMING = {
    "structured_json": "{basename}_structured.json",
    "section_summary": "{basename}_section_summary.json",
    "html_output": "{basename}.html",
    "markdown_output": "{basename}.md"
}

# Environment variable overrides
def load_env_config() -> Dict:
    """Load configuration overrides from environment variables."""
    env_config = {}

    # PDF processing overrides
    if scale := os.getenv("PDF_IMAGE_SCALE"):
        env_config["image_scale"] = float(scale)

    if output_dir := os.getenv("OUTPUT_DIR"):
        env_config["output_dir"] = Path(output_dir)

    if log_level := os.getenv("LOG_LEVEL"):
        env_config["log_level"] = log_level

    if max_memory := os.getenv("MAX_MEMORY_MB"):
        env_config["max_memory_mb"] = int(max_memory)

    return env_config

# Configuration validation
def validate_config() -> bool:
    """Validate configuration settings and return True if valid."""
    errors = []

    # Check required directories exist or can be created
    try:
        DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        errors.append(f"Cannot create output directory: {DEFAULT_OUTPUT_DIR}")

    # Validate numeric ranges
    if not 0.5 <= PDFProcessingConfig.IMAGE_SCALE <= 5.0:
        errors.append("IMAGE_SCALE must be between 0.5 and 5.0")

    if PerformanceConfig.MAX_MEMORY_MB < 512:
        errors.append("MAX_MEMORY_MB must be at least 512")

    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False

    return True

# Configuration factory
def get_config() -> Dict:
    """Get the complete configuration dictionary."""
    config = {
        "pdf_processing": PDFProcessingConfig.__dict__,
        "json": JSONConfig.__dict__,
        "html": HTMLConfig.__dict__,
        "markdown": MarkdownConfig.__dict__,
        "logging": LoggingConfig.__dict__,
        "performance": PerformanceConfig.__dict__,
        "features": FeatureFlags.__dict__,
        "file_formats": {
            "input": SUPPORTED_INPUT_FORMATS,
            "output": SUPPORTED_OUTPUT_FORMATS,
            "naming": FILE_NAMING
        },
        "paths": {
            "project_root": PROJECT_ROOT,
            "output_dir": DEFAULT_OUTPUT_DIR,
            "templates_dir": TEMPLATES_DIR
        }
    }

    # Apply environment overrides
    env_overrides = load_env_config()
    config.update(env_overrides)

    return config

# Initialize and validate configuration on import
if __name__ == "__main__":
    config = get_config()
    is_valid = validate_config()
    print(f"Configuration valid: {is_valid}")
