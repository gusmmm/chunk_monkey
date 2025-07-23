"""
Generators Package for Chunk Monkey
===================================

This package contains output generation modules for the Chunk Monkey pipeline.
It handles the creation of various output formats from structured document data.

Modules:
- html_generator: HTML visualization generation
- markdown_generator: Markdown output generation
- report_generator: Report and summary generation

Author: Chunk Monkey Team
"""

from .html_generator import HTMLGenerator

# Import convenience functions
from .html_generator import (
    generate_html,
    generate_html_from_json
)

__all__ = [
    'HTMLGenerator',
    'generate_html',
    'generate_html_from_json'
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Output generation modules for HTML, markdown, and reports"
