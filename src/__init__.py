"""
Chunk Monkey - PDF Processing Pipeline
=====================================

A comprehensive PDF processing pipeline that converts PDF documents into
structured data formats for AI/LLM processing and generates beautiful
HTML visualizations.

Main Components:
- processors: PDF and document processing modules
- generators: Output generation (HTML, markdown)
- utils: Utility functions and helpers
- config: Configuration management

Author: Chunk Monkey Team
"""

__version__ = "1.0.0"
__author__ = "Chunk Monkey Team"
__description__ = "PDF Processing Pipeline for AI and LLM Applications"

# Import main classes for convenience
from .processors.pdf_processor import PDFProcessor
from .generators.html_generator import HTMLGenerator
from .utils.file_utils import FileManager
from .utils.text_utils import TextProcessor
from .config.settings import get_config

# Define public API
__all__ = [
    'PDFProcessor',
    'HTMLGenerator',
    'FileManager',
    'TextProcessor',
    'get_config'
]

# Version information
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

def get_version():
    """Get version string."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return VERSION_INFO.copy()
