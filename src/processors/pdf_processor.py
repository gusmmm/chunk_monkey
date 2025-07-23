"""
PDF Processor Module for Chunk Monkey

This module handles PDF document processing using Docling, extracting text, images,
tables, and document structure while maintaining hierarchical relationships.

Key Features:
- High-quality PDF extraction with Docling
- Automatic section hierarchy detection
- Image and table extraction with base64 encoding
- References section detection
- Structured data output with metadata

Author: Chunk Monkey Team
"""

import json
import base64
import re
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import PictureItem, TableItem, TextItem, ListItem, ImageRefMode

try:
    from ..config.settings import PDFProcessingConfig, JSONConfig, LoggingConfig
    from ..utils.text_utils import TextProcessor
    from ..utils.file_utils import FileManager
except ImportError:
    # Handle both relative and absolute imports
    try:
        from config.settings import PDFProcessingConfig, JSONConfig, LoggingConfig
        from utils.text_utils import TextProcessor
        from utils.file_utils import FileManager
    except ImportError:
        import sys
        from pathlib import Path
        # Add src to path for standalone execution
        src_path = Path(__file__).parent.parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        from config.settings import PDFProcessingConfig, JSONConfig, LoggingConfig
        from utils.text_utils import TextProcessor
        from utils.file_utils import FileManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, LoggingConfig.LOG_LEVEL),
    format=LoggingConfig.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Main PDF processing class that handles document conversion and structure extraction.

    This class orchestrates the entire PDF processing pipeline:
    1. Configure Docling converter with optimal settings
    2. Process PDF and extract raw document structure
    3. Analyze document hierarchy and section relationships
    4. Extract and encode images, tables, and text content
    5. Generate structured JSON output with metadata
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize PDF processor with configuration.

        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.config = config or {}
        self.text_processor = TextProcessor()
        self.file_manager = FileManager()
        self.converter = self._configure_pipeline()

        # Processing state
        self.current_main_section = None
        self.current_subsection = None
        self.section_hierarchy = []
        self.in_references_section = False

        # Image/table counters for file naming
        self.table_counter = 0
        self.picture_counter = 0
        self.page_counter = 0

        logger.info("PDF Processor initialized with Docling backend")

    def _configure_pipeline(self) -> DocumentConverter:
        """
        Configure and return a DocumentConverter with optimal settings.

        Returns:
            DocumentConverter: Configured converter instance
        """
        # Create pipeline options with configuration
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = self.config.get(
            'image_scale',
            PDFProcessingConfig.IMAGE_SCALE
        )
        pipeline_options.generate_page_images = self.config.get(
            'generate_page_images',
            PDFProcessingConfig.GENERATE_PAGE_IMAGES
        )
        pipeline_options.generate_picture_images = self.config.get(
            'generate_picture_images',
            PDFProcessingConfig.GENERATE_PICTURE_IMAGES
        )
        pipeline_options.generate_table_images = self.config.get(
            'generate_table_images',
            PDFProcessingConfig.GENERATE_TABLE_IMAGES
        )

        # Configure OCR and quality settings
        if PDFProcessingConfig.OCR_ENABLED:
            # Additional OCR configuration would go here
            pass

        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def process_pdf(self, file_path: str, output_dir: Optional[str] = None) -> Any:
        """
        Process a PDF file and return the document object.

        Args:
            file_path: Path to the PDF file to process
            output_dir: Directory to save extracted images and files

        Returns:
            Document object from Docling processing

        Raises:
            Exception: If PDF processing fails
        """
        file_path = Path(file_path)

        # Validate input file
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not file_path.suffix.lower() == '.pdf':
            raise ValueError(f"File must be a PDF: {file_path}")

        # Check file size limits
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        max_size = self.config.get('max_file_size_mb', 100)
        if file_size_mb > max_size:
            raise ValueError(f"File too large: {file_size_mb:.1f}MB > {max_size}MB")

        logger.info(f"Processing PDF: {file_path} ({file_size_mb:.1f}MB)")

        try:
            conv_res = self.converter.convert(file_path)
            doc = conv_res.document

            # Store output directory and document filename for image extraction
            self.output_dir = Path(output_dir) if output_dir else Path("output")
            self.doc_filename = file_path.stem

            # Reset counters for each document
            self.table_counter = 0
            self.picture_counter = 0
            self.page_counter = 0

            logger.info(f"Successfully processed PDF with {len(list(doc.iterate_items()))} items")
            return doc

        except Exception as e:
            logger.error(f"Error processing PDF with Docling: {e}")
            raise

    def safe_get_text(self, item: Any) -> Optional[str]:
        """
        Safely extract text from an item, handling various attribute names.

        Args:
            item: Document item to extract text from

        Returns:
            Extracted text string or None if not found
        """
        return self.text_processor.safe_get_text(item)

    def safe_get_caption(self, item: Any) -> Optional[str]:
        """
        Safely extract caption from an item.

        Args:
            item: Document item to extract caption from

        Returns:
            Caption text or None if not found
        """
        return self.text_processor.safe_get_caption(item)

    def get_item_type(self, item: Any) -> str:
        """
        Get the type of an item as a string.

        Args:
            item: Document item to get type for

        Returns:
            String representation of item type
        """
        return type(item).__name__.lower()

    def is_references_section(self, item: Any) -> bool:
        """
        Check if an item indicates the start of a references/bibliography section.

        Args:
            item: Document item to check

        Returns:
            True if item indicates references section
        """
        if not PDFProcessingConfig.DETECT_REFERENCES:
            return False

        item_type = self.get_item_type(item)
        text = self.safe_get_text(item)

        if text and ('header' in item_type or 'heading' in item_type or 'section' in item_type):
            pattern = r'\b(' + '|'.join(PDFProcessingConfig.REFERENCE_KEYWORDS) + r')\b'
            return bool(re.search(pattern, text, re.IGNORECASE))

        return False

    def is_main_header(self, item: Any) -> bool:
        """
        Determine if an item is a main section header based on formatting and content.

        Args:
            item: Document item to analyze

        Returns:
            True if item is a main section header
        """
        item_type = self.get_item_type(item)
        text = self.safe_get_text(item)

        if not text or not ('header' in item_type or 'heading' in item_type or 'section' in item_type):
            return False

        # Check for main header indicators
        text_upper = text.upper()
        min_length = self.config.get('main_header_min_length', PDFProcessingConfig.MAIN_HEADER_MIN_LENGTH)

        # Main headers are typically:
        # 1. All caps or mostly caps
        # 2. Longer descriptive titles
        # 3. Common section keywords
        # 4. End with colons
        main_keywords = [
            'abstract', 'introduction', 'methods', 'methodology', 'results',
            'discussion', 'conclusion', 'references', 'bibliography',
            'acknowledgments', 'appendix', 'background', 'literature review',
            'analysis', 'findings', 'implications', 'limitations'
        ]

        # Check if it's a main header
        conditions = [
            len(text) > min_length,  # Long descriptive titles
            text.isupper(),  # All uppercase
            any(keyword in text.lower() for keyword in main_keywords),  # Contains main keywords
            text.endswith(':'),  # Ends with colon
            text.count(' ') >= 3  # Multi-word titles
        ]

        return any(conditions)

    def update_section_context(self, item: Any) -> None:
        """
        Update the current section context based on the item.

        Args:
            item: Document item to analyze for section information
        """
        item_type = self.get_item_type(item)

        # Check if this is a header/section item
        if 'header' in item_type or 'heading' in item_type or 'section' in item_type:
            text = self.safe_get_text(item)
            if not text:
                return

            if self.is_main_header(item):
                # This is a main section header
                self.current_main_section = text
                self.current_subsection = None
                self.section_hierarchy = [self.current_main_section]

                # Check if this is the references section
                if self.is_references_section(item):
                    self.in_references_section = True
                    logger.info(f"Detected references section: {text}")
                else:
                    self.in_references_section = False

                logger.debug(f"New main section: {text}")

            else:
                # This is a subsection header
                self.current_subsection = text
                if self.current_main_section:
                    self.section_hierarchy = [self.current_main_section, self.current_subsection]
                else:
                    self.section_hierarchy = [self.current_subsection]

                logger.debug(f"New subsection: {text}")

    def process_table_item(self, item: TableItem, doc: Any) -> Dict[str, Any]:
        """
        Process a TableItem and return its structured representation.

        Args:
            item: TableItem to process
            doc: Parent document object

        Returns:
            Dictionary containing table data and metadata
        """
        table_content = self.safe_get_text(item)

        # Fallback content extraction
        if not table_content:
            if hasattr(item, 'data'):
                table_content = str(item.data)
            elif hasattr(item, 'content'):
                table_content = str(item.content)
            else:
                table_content = str(item)

        return {
            "content": table_content,
            "caption": self.safe_get_caption(item),
            "item_type": self.get_item_type(item),
            "section_hierarchy": self.section_hierarchy.copy(),
            "parent_section": self.current_main_section,
            "subsection": self.current_subsection
        }

    def process_picture_item(self, item: PictureItem, doc: Any) -> Optional[Dict[str, Any]]:
        """
        Process a PictureItem and return its structured representation.

        Args:
            item: PictureItem to process
            doc: Parent document object

        Returns:
            Dictionary containing image data and metadata, or None if processing fails
        """
        try:
            self.picture_counter += 1

            # Save image as external file
            pil_image = item.get_image(doc)
            image_filename = f"{self.doc_filename}-picture-{self.picture_counter}.png"
            image_path = self.output_dir / image_filename

            # Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)

            # Optimize image if needed
            if hasattr(pil_image, 'size'):
                width, height = pil_image.size
                # Resize if too large (optional optimization)
                max_dimension = self.config.get('max_image_dimension', 2048)
                if max(width, height) > max_dimension:
                    ratio = max_dimension / max(width, height)
                    new_size = (int(width * ratio), int(height * ratio))
                    pil_image = pil_image.resize(new_size, resample=1)  # LANCZOS

            # Save image file
            pil_image.save(image_path, format="PNG", optimize=True)

            return {
                "image_filename": image_filename,
                "image_path": str(image_path),
                "caption": self.safe_get_caption(item),
                "item_type": self.get_item_type(item),
                "section_hierarchy": self.section_hierarchy.copy(),
                "parent_section": self.current_main_section,
                "subsection": self.current_subsection
            }

        except Exception as e:
            logger.warning(f"Error processing image: {e}")
            return None

    def process_text_item(self, item: Any) -> Optional[Dict[str, Any]]:
        """
        Process a text-based item and return its structured representation.

        Args:
            item: Text item to process

        Returns:
            Dictionary containing text data and metadata, or None if no valid text
        """
        text = self.safe_get_text(item)

        # Apply minimum length filter
        min_length = self.config.get('min_text_length', JSONConfig.MIN_TEXT_LENGTH)
        if not text or len(text.strip()) < min_length:
            return None

        # Clean and normalize text
        text = self.text_processor.clean_text(text)

        return {
            "type": self.get_item_type(item),
            "text": text,
            "section_hierarchy": self.section_hierarchy.copy(),
            "parent_section": self.current_main_section,
            "subsection": self.current_subsection
        }

    def initialize_structure(self) -> Dict[str, Any]:
        """
        Initialize the structured data dictionary with metadata.

        Returns:
            Empty structured data dictionary with metadata section
        """
        return {
            "metadata": {
                "total_items": 0,
                "processing_timestamp": None,
                "processor_version": "1.0.0",
                "docling_version": None,  # Could be extracted from docling
                "configuration": {
                    "image_scale": self.config.get('image_scale', PDFProcessingConfig.IMAGE_SCALE),
                    "detect_references": PDFProcessingConfig.DETECT_REFERENCES,
                    "min_text_length": self.config.get('min_text_length', JSONConfig.MIN_TEXT_LENGTH)
                }
            },
            "content": [],
            "tables": [],
            "images": [],
            "references": []
        }

    def extract_structured_data(self, doc: Any) -> Dict[str, Any]:
        """
        Extract and structure content from the document.

        This is the main processing method that iterates through all document
        items and organizes them into a hierarchical structure.

        Args:
            doc: Docling document object to process

        Returns:
            Structured data dictionary with content, tables, images, and references
        """
        structured_data = self.initialize_structure()
        item_count = 0

        # Reset processing state
        self.current_main_section = None
        self.current_subsection = None
        self.section_hierarchy = []
        self.in_references_section = False

        logger.info("Extracting and structuring document content...")

        try:
            # Process all document items
            for item, _ in doc.iterate_items():
                item_count += 1

                # Update section context
                self.update_section_context(item)

                # Process items based on type and context
                if self.in_references_section:
                    # Handle references section
                    text_data = self.process_text_item(item)
                    if text_data:
                        structured_data["references"].append(text_data)

                elif isinstance(item, TableItem):
                    # Handle tables
                    table_data = self.process_table_item(item, doc)
                    table_data["label"] = f"table_{len(structured_data['tables']) + 1}"
                    structured_data["tables"].append(table_data)

                elif isinstance(item, PictureItem):
                    # Handle images
                    image_data = self.process_picture_item(item, doc)
                    if image_data:
                        image_data["label"] = f"image_{len(structured_data['images']) + 1}"
                        structured_data["images"].append(image_data)

                else:
                    # Handle regular text content
                    text_data = self.process_text_item(item)
                    if text_data:
                        structured_data["content"].append(text_data)

                # Progress logging
                if item_count % 50 == 0:
                    logger.debug(f"Processed {item_count} items...")

        except Exception as e:
            logger.error(f"Error during document processing: {e}")
            raise

        # Update metadata
        structured_data["metadata"]["total_items"] = item_count
        structured_data["metadata"]["processing_timestamp"] = datetime.now().isoformat()

        # Log processing summary
        logger.info(f"Document processing complete:")
        logger.info(f"  Total items: {item_count}")
        logger.info(f"  Content items: {len(structured_data['content'])}")
        logger.info(f"  Tables: {len(structured_data['tables'])}")
        logger.info(f"  Images: {len(structured_data['images'])}")
        logger.info(f"  References: {len(structured_data['references'])}")

        return structured_data

    def get_section_summary(self, data: Dict) -> Dict[str, Dict]:
        """
        Generate a summary of all sections and their content counts.

        Args:
            data: Structured data dictionary

        Returns:
            Dictionary mapping section names to content statistics
        """
        sections = {}

        for category in ["content", "tables", "images", "references"]:
            for item in data.get(category, []):
                parent = item.get("parent_section", "Unknown")
                subsection = item.get("subsection")

                if parent not in sections:
                    sections[parent] = {
                        "content_count": 0,
                        "table_count": 0,
                        "image_count": 0,
                        "reference_count": 0,
                        "subsections": set()
                    }

                # Map category names to count keys
                count_key_map = {
                    "content": "content_count",
                    "tables": "table_count",
                    "images": "image_count",
                    "references": "reference_count"
                }

                sections[parent][count_key_map[category]] += 1

                if subsection:
                    sections[parent]["subsections"].add(subsection)

        # Convert sets to lists for JSON serialization
        for section in sections.values():
            section["subsections"] = sorted(list(section["subsections"]))

        return sections

    def filter_by_section(self, data: Dict, section_name: str) -> Dict[str, List]:
        """
        Filter the structured data to return only items from a specific section.

        Args:
            data: Structured data dictionary
            section_name: Name of section to filter by

        Returns:
            Filtered data dictionary containing only specified section
        """
        filtered_data = {
            "content": [],
            "tables": [],
            "images": [],
            "references": []
        }

        section_name_lower = section_name.lower()

        for category in ["content", "tables", "images", "references"]:
            for item in data.get(category, []):
                # Check if the section name matches any level in the hierarchy
                if item.get("section_hierarchy"):
                    for section in item["section_hierarchy"]:
                        if section_name_lower in section.lower():
                            filtered_data[category].append(item)
                            break
                # Also check parent_section for direct matches
                elif (item.get("parent_section") and
                      section_name_lower in item["parent_section"].lower()):
                    filtered_data[category].append(item)

        return filtered_data

    def save_to_json(self, data: Dict, filename: str) -> None:
        """
        Save structured data to a JSON file with proper formatting.

        Args:
            data: Data dictionary to save
            filename: Output filename

        Raises:
            Exception: If file writing fails
        """
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    data,
                    f,
                    indent=JSONConfig.INDENT_SIZE,
                    ensure_ascii=JSONConfig.ENSURE_ASCII
                )

            logger.info(f"Successfully saved structured data to {output_path}")

        except Exception as e:
            logger.error(f"Error saving JSON file: {e}")
            raise

    def process_document(self, file_path: str, output_dir: Optional[str] = None) -> Tuple[Dict, str]:
        """
        Complete document processing pipeline from PDF to structured JSON.

        Args:
            file_path: Path to input PDF file
            output_dir: Optional output directory (defaults to config)

        Returns:
            Tuple of (structured_data, output_filename)
        """
        try:
            # Process the PDF
            doc = self.process_pdf(file_path)

            # Extract structured data
            structured_data = self.extract_structured_data(doc)

            # Determine output filename
            file_stem = Path(file_path).stem
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = Path("output")

            output_path.mkdir(parents=True, exist_ok=True)
            output_filename = output_path / f"{file_stem}_structured.json"

            # Save structured data
            self.save_to_json(structured_data, str(output_filename))

            # Generate and save section summary
            section_summary = self.get_section_summary(structured_data)
            summary_filename = output_path / f"{file_stem}_section_summary.json"
            self.save_to_json(section_summary, str(summary_filename))

            logger.info(f"Document processing pipeline completed successfully")
            logger.info(f"Output files: {output_filename}, {summary_filename}")

            return structured_data, str(output_filename)

        except Exception as e:
            logger.error(f"Error in document processing pipeline: {e}")
            raise


    def process_pdf_with_images(self, file_path: str, output_dir: Optional[str] = None) -> Tuple[Any, str]:
        """
        Enhanced PDF processing with image extraction following Docling best practices.

        Args:
            file_path: Path to input PDF file
            output_dir: Optional output directory (defaults to "output")

        Returns:
            Tuple of (document, output_directory_path)
        """
        file_path = Path(file_path)

        # Set up output directory
        if not output_dir:
            output_dir = "output"
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Store for use in image saving
        self.output_dir = output_path
        self.doc_filename = file_path.stem

        # Reset counters
        self.table_counter = 0
        self.picture_counter = 0

        logger.info(f"Processing PDF with image extraction: {file_path}")

        try:
            # Process PDF with Docling
            conv_res = self.converter.convert(file_path)
            doc = conv_res.document

            # Save individual images from tables and pictures
            self._save_document_images(conv_res)

            # Generate markdown files
            self._save_markdown_outputs(conv_res, output_path)

            # Generate HTML with image references
            self._save_html_output(conv_res, output_path)

            logger.info(f"Successfully processed PDF with images saved to: {output_path}")
            return doc, str(output_path)

        except Exception as e:
            logger.error(f"Error in enhanced PDF processing: {e}")
            raise

    def _save_document_images(self, conv_res: Any) -> None:
        """Save individual images from tables and pictures."""
        # Save images of figures and tables
        for element, _level in conv_res.document.iterate_items():
            if isinstance(element, TableItem):
                self.table_counter += 1
                element_image_filename = (
                    self.output_dir / f"{self.doc_filename}-table-{self.table_counter}.png"
                )
                with element_image_filename.open("wb") as fp:
                    element.get_image(conv_res.document).save(fp, "PNG")
                logger.debug(f"Saved table image: {element_image_filename}")

            if isinstance(element, PictureItem):
                self.picture_counter += 1
                element_image_filename = (
                    self.output_dir / f"{self.doc_filename}-picture-{self.picture_counter}.png"
                )
                with element_image_filename.open("wb") as fp:
                    element.get_image(conv_res.document).save(fp, "PNG")
                logger.debug(f"Saved picture image: {element_image_filename}")

    def _save_markdown_outputs(self, conv_res: Any, output_path: Path) -> None:
        """Save markdown files with different image reference modes."""
        # Save markdown with embedded pictures (base64)
        md_embedded_filename = output_path / f"{self.doc_filename}-with-images.md"
        conv_res.document.save_as_markdown(md_embedded_filename, image_mode=ImageRefMode.EMBEDDED)
        logger.info(f"Saved markdown with embedded images: {md_embedded_filename}")

        # Save markdown with externally referenced pictures
        md_refs_filename = output_path / f"{self.doc_filename}-with-image-refs.md"
        conv_res.document.save_as_markdown(md_refs_filename, image_mode=ImageRefMode.REFERENCED)
        logger.info(f"Saved markdown with image references: {md_refs_filename}")

        # Also save a simple markdown file for compatibility
        md_simple_filename = output_path / f"{self.doc_filename}.md"
        conv_res.document.save_as_markdown(md_simple_filename, image_mode=ImageRefMode.REFERENCED)
        logger.info(f"Saved simple markdown: {md_simple_filename}")

    def _save_html_output(self, conv_res: Any, output_path: Path) -> None:
        """Save HTML with externally referenced images."""
        html_filename = output_path / f"{self.doc_filename}-docling.html"
        conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)
        logger.info(f"Saved HTML with image references: {html_filename}")

    def process_complete_pipeline(self, file_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Complete pipeline: PDF -> Images + Markdown + JSON + HTML

        Args:
            file_path: Path to input PDF file
            output_dir: Optional output directory

        Returns:
            Dictionary with paths to all generated files
        """
        try:
            # Enhanced PDF processing with images
            doc, output_path = self.process_pdf_with_images(file_path, output_dir)

            # Extract structured data for custom JSON/HTML
            structured_data = self.extract_structured_data(doc)

            # Save custom structured JSON
            json_filename = Path(output_path) / f"{Path(file_path).stem}_structured.json"
            self.save_to_json(structured_data, str(json_filename))

            return {
                'output_directory': output_path,
                'markdown_embedded': str(Path(output_path) / f"{Path(file_path).stem}-with-images.md"),
                'markdown_refs': str(Path(output_path) / f"{Path(file_path).stem}-with-image-refs.md"),
                'markdown_simple': str(Path(output_path) / f"{Path(file_path).stem}.md"),
                'html_docling': str(Path(output_path) / f"{Path(file_path).stem}-docling.html"),
                'json_structured': str(json_filename),
                'images_extracted': f"Tables: {self.table_counter}, Pictures: {self.picture_counter}"
            }

        except Exception as e:
            logger.error(f"Error in complete pipeline: {e}")
            raise


# Convenience functions for backward compatibility
def process_pdf(file_path: str) -> Any:
    """Convenience function to process PDF with default settings."""
    processor = PDFProcessor()
    return processor.process_pdf(file_path)


def extract_structured_data(doc: Any) -> Dict[str, Any]:
    """Convenience function to extract structured data with default settings."""
    processor = PDFProcessor()
    return processor.extract_structured_data(doc)


def main():
    """Main function for command-line usage."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python pdf_processor.py <pdf_file>")
        sys.exit(1)

    pdf_file = sys.argv[1]

    try:
        processor = PDFProcessor()
        structured_data, output_file = processor.process_document(pdf_file)

        print(f"\nProcessing completed successfully!")
        print(f"Structured data saved to: {output_file}")
        print(f"Total content items: {len(structured_data['content'])}")
        print(f"Tables found: {len(structured_data['tables'])}")
        print(f"Images found: {len(structured_data['images'])}")
        print(f"References found: {len(structured_data['references'])}")

    except Exception as e:
        print(f"Error processing PDF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
