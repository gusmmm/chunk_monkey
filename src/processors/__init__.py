"""
Processors Package for Chunk Monkey
===================================

This package contains document processing modules for the Chunk Monkey pipeline.
It handles PDF processing, markdown parsing, and data structuring operations.

Modules:
- pdf_processor: Main PDF processing with Docling
- markdown_parser: Markdown structure parsing
- json_structurer: JSON data structuring and organization

Author: Chunk Monkey Team
"""

from .pdf_processor import PDFProcessor

# Import convenience functions
from .pdf_processor import (
    process_pdf,
    extract_structured_data
)

__all__ = [
    'PDFProcessor',
    'process_pdf',
    'extract_structured_data'
]

# Package metadata
__version__ = "1.0.0"
__description__ = "Document processing modules for PDF and text analysis"
