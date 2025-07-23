"""
Text Processing Utilities for Chunk Monkey

This module provides utility functions for text processing, cleaning, and extraction
from various document elements. It handles common text processing tasks like
cleaning, normalization, and safe extraction from document items.

Key Features:
- Safe text extraction from various item types
- Text cleaning and normalization
- Caption extraction from complex objects
- Unicode handling and encoding
- Text validation and filtering

Author: Chunk Monkey Team
"""

import re
import logging
from typing import Any, Optional, List, Dict
import unicodedata
from html import unescape

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Text processing utility class with methods for cleaning, extracting,
    and normalizing text content from document items.
    """

    def __init__(self):
        """Initialize text processor with default settings."""
        # Common text attribute names to try when extracting text
        self.text_attributes = ['text', 'content', 'value', 'data', 'caption']

        # Patterns for text cleaning
        self.whitespace_pattern = re.compile(r'\s+')
        self.special_chars_pattern = re.compile(r'[^\w\s\-.,;:!?()[\]{}"\']')
        self.multiple_punctuation_pattern = re.compile(r'([.!?]){2,}')

        # Common section keywords for header detection
        self.section_keywords = {
            'main_sections': [
                'abstract', 'introduction', 'background', 'literature review',
                'methodology', 'methods', 'materials and methods',
                'results', 'findings', 'analysis', 'discussion',
                'conclusion', 'conclusions', 'implications', 'limitations',
                'future work', 'references', 'bibliography', 'acknowledgments',
                'appendix', 'appendices'
            ],
            'reference_keywords': [
                'references', 'bibliography', 'citations', 'works cited',
                'literature cited', 'sources'
            ]
        }

    def safe_get_text(self, item: Any) -> Optional[str]:
        """
        Safely extract text from an item, handling various attribute names.

        This method tries multiple common attribute names and handles
        different object types gracefully.

        Args:
            item: Document item to extract text from

        Returns:
            Extracted text string or None if not found
        """
        if item is None:
            return None

        # Try common text attributes
        for attr in self.text_attributes:
            if hasattr(item, attr):
                try:
                    value = getattr(item, attr)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
                    elif hasattr(value, '__str__') and str(value).strip():
                        return str(value).strip()
                except (AttributeError, TypeError):
                    continue

        # Try converting the entire object to string as fallback
        try:
            text = str(item).strip()
            if text and text != str(type(item)):
                return text
        except (TypeError, AttributeError):
            pass

        return None

    def safe_get_caption(self, item: Any) -> Optional[str]:
        """
        Safely extract caption from an item.

        Handles various caption structures including lists and nested objects.

        Args:
            item: Document item to extract caption from

        Returns:
            Caption text or None if not found
        """
        if item is None:
            return None

        try:
            # Try direct caption attribute
            if hasattr(item, 'caption'):
                caption = item.caption
                if isinstance(caption, str) and caption.strip():
                    return caption.strip()
                elif hasattr(caption, 'text'):
                    caption_text = self.safe_get_text(caption)
                    if caption_text:
                        return caption_text

            # Try captions list (multiple captions)
            if hasattr(item, 'captions') and item.captions:
                for caption in item.captions:
                    caption_text = self.safe_get_text(caption)
                    if caption_text:
                        return caption_text

            # Try alternative caption attributes
            for attr in ['title', 'label', 'description', 'alt', 'alt_text']:
                if hasattr(item, attr):
                    value = getattr(item, attr)
                    if isinstance(value, str) and value.strip():
                        return value.strip()

        except (AttributeError, IndexError, TypeError) as e:
            logger.debug(f"Error extracting caption: {e}")

        return None

    def clean_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text to clean
            aggressive: Whether to apply aggressive cleaning

        Returns:
            Cleaned text string
        """
        if not text:
            return ""

        # Basic cleaning
        cleaned = text.strip()

        # Handle HTML entities
        cleaned = unescape(cleaned)

        # Normalize Unicode characters
        cleaned = unicodedata.normalize('NFKC', cleaned)

        # Normalize whitespace
        cleaned = self.whitespace_pattern.sub(' ', cleaned)

        if aggressive:
            # Remove special characters (keep basic punctuation)
            cleaned = self.special_chars_pattern.sub('', cleaned)

            # Fix multiple punctuation
            cleaned = self.multiple_punctuation_pattern.sub(r'\1', cleaned)

        # Remove excessive line breaks
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Final trim
        return cleaned.strip()

    def extract_headings(self, text: str) -> List[str]:
        """
        Extract potential headings from text based on formatting patterns.

        Args:
            text: Text to analyze for headings

        Returns:
            List of potential heading strings
        """
        headings = []

        if not text:
            return headings

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for heading patterns
            is_heading = (
                line.isupper() or  # All uppercase
                line.endswith(':') or  # Ends with colon
                (len(line.split()) <= 10 and len(line) > 10) or  # Short descriptive
                any(keyword in line.lower() for keyword in self.section_keywords['main_sections'])
            )

            if is_heading:
                headings.append(line)

        return headings

    def is_section_header(self, text: str, item_type: str = "") -> bool:
        """
        Determine if text represents a section header.

        Args:
            text: Text to analyze
            item_type: Type of the item containing the text

        Returns:
            True if text appears to be a section header
        """
        if not text:
            return False

        text_lower = text.lower().strip()

        # Check item type indicators
        if any(header_type in item_type.lower() for header_type in ['header', 'heading', 'section']):
            return True

        # Check for section keywords
        if any(keyword in text_lower for keyword in self.section_keywords['main_sections']):
            return True

        # Check formatting patterns
        formatting_indicators = [
            text.isupper(),  # All uppercase
            text.endswith(':'),  # Ends with colon
            len(text) > 20 and len(text.split()) >= 3,  # Multi-word descriptive
            re.match(r'^[A-Z][A-Z\s]+$', text),  # Title case pattern
        ]

        return any(formatting_indicators)

    def is_reference_section(self, text: str, item_type: str = "") -> bool:
        """
        Check if text indicates a references/bibliography section.

        Args:
            text: Text to check
            item_type: Type of the item containing the text

        Returns:
            True if text indicates references section
        """
        if not text:
            return False

        # Must be a header-type item
        if not any(header_type in item_type.lower() for header_type in ['header', 'heading', 'section']):
            return False

        text_lower = text.lower().strip()

        # Check for reference keywords
        return any(keyword in text_lower for keyword in self.section_keywords['reference_keywords'])

    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text using simple sentence boundary detection.

        Args:
            text: Text to split into sentences

        Returns:
            List of sentence strings
        """
        if not text:
            return []

        # Simple sentence splitting pattern
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)

        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short sentences
                cleaned_sentences.append(sentence)

        return cleaned_sentences

    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract potential keywords from text.

        Args:
            text: Text to analyze
            min_length: Minimum length for keywords

        Returns:
            List of keyword strings
        """
        if not text:
            return []

        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter common stop words (simple list)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }

        # Filter and collect keywords
        keywords = []
        for word in words:
            if (len(word) >= min_length and
                word not in stop_words and
                not word.isdigit()):
                keywords.append(word)

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)

        return unique_keywords

    def truncate_text(self, text: str, max_length: int = 200, ellipsis: str = "...") -> str:
        """
        Truncate text to a maximum length, preserving word boundaries.

        Args:
            text: Text to truncate
            max_length: Maximum length of output
            ellipsis: String to append when truncating

        Returns:
            Truncated text string
        """
        if not text or len(text) <= max_length:
            return text

        # Find the last space before the limit
        truncate_at = text.rfind(' ', 0, max_length - len(ellipsis))

        if truncate_at == -1:
            # No space found, hard truncate
            truncate_at = max_length - len(ellipsis)

        return text[:truncate_at] + ellipsis

    def normalize_spacing(self, text: str) -> str:
        """
        Normalize spacing in text, handling various whitespace characters.

        Args:
            text: Text to normalize

        Returns:
            Text with normalized spacing
        """
        if not text:
            return ""

        # Replace various whitespace characters with standard space
        normalized = re.sub(r'[\t\r\f\v]', ' ', text)

        # Collapse multiple spaces
        normalized = re.sub(r' {2,}', ' ', normalized)

        # Normalize line breaks
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)

        return normalized.strip()

    def detect_language(self, text: str) -> str:
        """
        Simple language detection based on character patterns.

        Note: This is a basic implementation. For production use,
        consider using a proper language detection library.

        Args:
            text: Text to analyze

        Returns:
            Detected language code (defaults to 'en')
        """
        if not text:
            return 'en'

        # Very basic language detection
        # Count non-ASCII characters
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        total_chars = len(text)

        if total_chars == 0:
            return 'en'

        ascii_ratio = ascii_chars / total_chars

        # If mostly ASCII, assume English
        if ascii_ratio > 0.9:
            return 'en'
        else:
            # For non-ASCII text, return unknown
            return 'unknown'

    def get_text_statistics(self, text: str) -> Dict[str, int]:
        """
        Get basic statistics about text content.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {
                'characters': 0,
                'words': 0,
                'sentences': 0,
                'paragraphs': 0,
                'lines': 0
            }

        # Basic counts
        char_count = len(text)
        word_count = len(re.findall(r'\b\w+\b', text))
        sentence_count = len(self.extract_sentences(text))
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        line_count = len(text.split('\n'))

        return {
            'characters': char_count,
            'words': word_count,
            'sentences': sentence_count,
            'paragraphs': paragraph_count,
            'lines': line_count
        }


# Convenience functions for direct use
def clean_text(text: str, aggressive: bool = False) -> str:
    """Convenience function for text cleaning."""
    processor = TextProcessor()
    return processor.clean_text(text, aggressive)


def safe_get_text(item: Any) -> Optional[str]:
    """Convenience function for safe text extraction."""
    processor = TextProcessor()
    return processor.safe_get_text(item)


def safe_get_caption(item: Any) -> Optional[str]:
    """Convenience function for safe caption extraction."""
    processor = TextProcessor()
    return processor.safe_get_caption(item)
