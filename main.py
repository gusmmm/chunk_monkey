#!/usr/bin/env python3
"""
Chunk Monkey - PDF Processing Pipeline

A clean, professional tool for processing PDF documents into structured JSON
and beautiful HTML visualizations.

Usage:
    python main.py process <pdf_file>     # Full pipeline: PDF -> JSON -> HTML
    python main.py json <pdf_file>        # PDF -> JSON only
    python main.py html <json_file>       # JSON -> HTML only
    python main.py batch <input_dir>      # Batch process directory

Author: Chunk Monkey Team
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add src to Python path for clean imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from processors.pdf_processor import PDFProcessor
from generators.html_generator import HTMLGenerator
from utils.file_utils import FileManager
from config.settings import DEFAULT_OUTPUT_DIR


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('chunk_monkey.log')
        ]
    )


class ChunkMonkey:
    """Main application class for PDF processing pipeline."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize ChunkMonkey with optional output directory."""
        self.output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
        self.output_dir.mkdir(exist_ok=True)

        # Initialize processors
        self.pdf_processor = PDFProcessor()
        self.html_generator = HTMLGenerator()
        self.file_manager = FileManager()

        self.logger = logging.getLogger(__name__)

    def process_pdf_to_json(self, pdf_path: Path) -> Path:
        """Process PDF file with image extraction and generate structured JSON."""
        self.logger.info(f"Processing PDF with image extraction: {pdf_path}")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Enhanced PDF processing with images and markdown
        doc, output_path = self.pdf_processor.process_pdf_with_images(str(pdf_path), str(self.output_dir))
        structured_data = self.pdf_processor.extract_structured_data(doc)

        # Save JSON
        json_filename = f"{pdf_path.stem}_structured.json"
        json_path = self.output_dir / json_filename

        self.file_manager.write_json_file(json_path, structured_data)
        self.logger.info(f"JSON saved: {json_path}")
        self.logger.info(f"Markdown and images saved to: {output_path}")

        return json_path

    def generate_html_from_json(self, json_path: Path) -> Path:
        """Generate HTML visualization from JSON file."""
        self.logger.info(f"Generating HTML from: {json_path}")

        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        # Load JSON data
        structured_data = self.file_manager.read_json_file(json_path)

        # Generate HTML
        html_content = self.html_generator.generate_html_document(structured_data)

        # Save HTML
        html_filename = f"{json_path.stem.replace('_structured', '')}_output.html"
        html_path = self.output_dir / html_filename

        self.file_manager.write_text_file(html_path, html_content)
        self.logger.info(f"HTML saved: {html_path}")

        return html_path

    def process_full_pipeline(self, pdf_path: Path) -> tuple[Path, Path]:
        """Run the complete PDF -> Images + Markdown + JSON -> HTML pipeline."""
        self.logger.info(f"Starting enhanced pipeline for: {pdf_path}")

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Complete pipeline with images, markdown, and structured data
        results = self.pdf_processor.process_complete_pipeline(str(pdf_path), str(self.output_dir))

        json_path = Path(results['json_structured'])

        # Generate custom HTML visualization
        html_path = self.generate_html_from_json(json_path)

        self.logger.info("Enhanced pipeline completed successfully!")
        self.logger.info(f"Generated files:")
        for key, value in results.items():
            if key != 'output_directory':
                self.logger.info(f"  {key}: {value}")

        return json_path, html_path

    def batch_process(self, input_dir: Path) -> None:
        """Process all PDF files in a directory."""
        input_dir = Path(input_dir)
        if not input_dir.exists() or not input_dir.is_dir():
            raise ValueError(f"Input directory not found: {input_dir}")

        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            self.logger.warning(f"No PDF files found in: {input_dir}")
            return

        self.logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            try:
                self.logger.info(f"Processing: {pdf_file.name}")
                self.process_full_pipeline(pdf_file)
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_file.name}: {e}")
                continue

        self.logger.info("Batch processing completed!")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Chunk Monkey - PDF Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py process document.pdf          # Full pipeline
  python main.py json document.pdf             # PDF to JSON only
  python main.py html structured.json          # JSON to HTML only
  python main.py batch input_directory/        # Process all PDFs in directory
        """
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory (default: ./output)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process command (full pipeline)
    process_parser = subparsers.add_parser(
        "process",
        help="Run full pipeline: PDF -> JSON -> HTML"
    )
    process_parser.add_argument("pdf_file", type=Path, help="PDF file to process")

    # JSON command (PDF to JSON only)
    json_parser = subparsers.add_parser(
        "json",
        help="Convert PDF to structured JSON"
    )
    json_parser.add_argument("pdf_file", type=Path, help="PDF file to process")

    # HTML command (JSON to HTML only)
    html_parser = subparsers.add_parser(
        "html",
        help="Generate HTML from structured JSON"
    )
    html_parser.add_argument("json_file", type=Path, help="JSON file to process")

    # Batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Process all PDF files in a directory"
    )
    batch_parser.add_argument("input_dir", type=Path, help="Directory containing PDF files")

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return

    try:
        # Initialize ChunkMonkey
        chunk_monkey = ChunkMonkey(output_dir=args.output)

        # Execute command
        if args.command == "process":
            json_path, html_path = chunk_monkey.process_full_pipeline(args.pdf_file)
            print(f"\n✅ Pipeline completed successfully!")
            print(f"📄 JSON: {json_path}")
            print(f"🌐 HTML: {html_path}")

        elif args.command == "json":
            json_path = chunk_monkey.process_pdf_to_json(args.pdf_file)
            print(f"\n✅ JSON generated successfully!")
            print(f"📄 JSON: {json_path}")

        elif args.command == "html":
            html_path = chunk_monkey.generate_html_from_json(args.json_file)
            print(f"\n✅ HTML generated successfully!")
            print(f"🌐 HTML: {html_path}")

        elif args.command == "batch":
            chunk_monkey.batch_process(args.input_dir)
            print(f"\n✅ Batch processing completed!")
            print(f"📁 Check output directory: {chunk_monkey.output_dir}")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
