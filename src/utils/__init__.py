"""
Utils Package for Chunk Monkey
===============================

This package contains utility modules for the Chunk Monkey pipeline.
It provides helper functions for common operations like file management,
text processing, image handling, and configuration management.

Modules:
- file_utils: File operations and path management
- text_utils: Text processing and cleaning utilities
- image_utils: Image handling and conversion utilities
- section_filter: Content filtering and section management

Author: Chunk Monkey Team
"""

from .file_utils import FileManager
from .text_utils import TextProcessor

# Import convenience functions
from .file_utils import (
    ensure_directory,
    read_json_file,
    write_json_file,
    get_file_info
)

from .text_utils import (
    clean_text,
    safe_get_text,
    safe_get_caption
)

__all__ = [
    'FileManager',
    'TextProcessor',
    'ensure_directory',
    'read_json_file',
    'write_json_file',
    'get_file_info',
    'clean_text',
    'safe_get_text',
    'safe_get_caption'
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Utility modules for file operations, text processing, and helpers"
