#!/usr/bin/env python3
"""
Chunk Monkey Implementation Test Suite
======================================

This script thoroughly tests the new Chunk Monkey implementation to ensure
all components are working correctly. It validates installation, tests core
functionality, and provides detailed feedback.

Usage:
    uv run python test_implementation.py

    or with options:
    uv run python test_implementation.py --verbose --create-sample

Author: Chunk Monkey Team
"""

import sys
import os
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import traceback
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from processors.pdf_processor import PDFProcessor
    from generators.html_generator import HTMLGenerator
    from utils.file_utils import FileManager
    from utils.text_utils import TextProcessor
    from config.settings import get_config, validate_config
except ImportError as e:
    print(f"❌ Failed to import core modules: {e}")
    print("Make sure you're running from the chunk_monkey directory with:")
    print("uv run python test_implementation.py")
    sys.exit(1)


class TestResults:
    """Class to track and report test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
        self.warnings = []

    def pass_test(self, test_name: str, message: str = ""):
        """Record a passed test."""
        self.passed += 1
        print(f"✅ {test_name}: {message}")

    def fail_test(self, test_name: str, error: str, exception: Optional[Exception] = None):
        """Record a failed test."""
        self.failed += 1
        error_msg = f"❌ {test_name}: {error}"
        print(error_msg)
        self.errors.append(error_msg)
        if exception and hasattr(exception, '__traceback__'):
            print(f"   Exception: {str(exception)}")

    def skip_test(self, test_name: str, reason: str):
        """Record a skipped test."""
        self.skipped += 1
        print(f"⏭️  {test_name}: SKIPPED - {reason}")

    def warn(self, message: str):
        """Add a warning."""
        warning_msg = f"⚠️  WARNING: {message}"
        print(warning_msg)
        self.warnings.append(warning_msg)

    def summary(self) -> Dict:
        """Get test summary."""
        total = self.passed + self.failed + self.skipped
        return {
            'total': total,
            'passed': self.passed,
            'failed': self.failed,
            'skipped': self.skipped,
            'success_rate': (self.passed / total * 100) if total > 0 else 0,
            'errors': self.errors,
            'warnings': self.warnings
        }


def create_sample_pdf(output_path: str) -> bool:
    """Create a simple sample PDF for testing."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        c = canvas.Canvas(output_path, pagesize=letter)

        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Sample Test Document")

        # Add sections
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 700, "Introduction")

        c.setFont("Helvetica", 12)
        c.drawString(100, 680, "This is a sample PDF document created for testing the Chunk Monkey pipeline.")
        c.drawString(100, 660, "It contains multiple sections with different types of content.")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 620, "Methods")

        c.setFont("Helvetica", 12)
        c.drawString(100, 600, "The testing methodology includes:")
        c.drawString(120, 580, "• PDF processing with Docling")
        c.drawString(120, 560, "• Structure extraction and analysis")
        c.drawString(120, 540, "• HTML generation and visualization")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 500, "Results")

        c.setFont("Helvetica", 12)
        c.drawString(100, 480, "The results demonstrate successful processing of PDF documents.")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 440, "References")

        c.setFont("Helvetica", 12)
        c.drawString(100, 420, "1. Chunk Monkey Documentation")
        c.drawString(100, 400, "2. Docling Library Reference")

        c.save()
        return True

    except ImportError:
        return False
    except Exception:
        return False


def test_imports(results: TestResults) -> None:
    """Test that all core modules can be imported."""
    print("\n" + "="*60)
    print("Testing Module Imports")
    print("="*60)

    modules = [
        ("processors.pdf_processor", "PDFProcessor"),
        ("generators.html_generator", "HTMLGenerator"),
        ("utils.file_utils", "FileManager"),
        ("utils.text_utils", "TextProcessor"),
        ("config.settings", "get_config"),
    ]

    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            results.pass_test(f"Import {module_name}", f"{class_name} available")
        except ImportError as e:
            results.fail_test(f"Import {module_name}", f"Import failed: {e}")
        except AttributeError as e:
            results.fail_test(f"Import {module_name}", f"Class {class_name} not found: {e}")


def test_configuration(results: TestResults) -> None:
    """Test configuration system."""
    print("\n" + "="*60)
    print("Testing Configuration System")
    print("="*60)

    try:
        config = get_config()
        results.pass_test("Configuration Loading", "Config loaded successfully")

        # Check required sections
        required_sections = ['pdf_processing', 'json', 'html', 'logging']
        for section in required_sections:
            if section in config:
                results.pass_test(f"Config Section: {section}", "Present")
            else:
                results.fail_test(f"Config Section: {section}", "Missing")

        # Test validation
        is_valid = validate_config()
        if is_valid:
            results.pass_test("Configuration Validation", "All settings valid")
        else:
            results.fail_test("Configuration Validation", "Validation failed")

    except Exception as e:
        results.fail_test("Configuration System", f"Error: {e}", e)


def test_file_utils(results: TestResults) -> None:
    """Test file utility functions."""
    print("\n" + "="*60)
    print("Testing File Utilities")
    print("="*60)

    try:
        file_manager = FileManager()

        # Test directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test_subdir"
            created_dir = file_manager.ensure_directory(test_dir)

            if created_dir.exists():
                results.pass_test("Directory Creation", "Successfully created directory")
            else:
                results.fail_test("Directory Creation", "Failed to create directory")

            # Test JSON operations
            test_data = {"test": "data", "numbers": [1, 2, 3]}
            json_file = created_dir / "test.json"

            # Write JSON
            file_manager.write_json_file(json_file, test_data)
            if json_file.exists():
                results.pass_test("JSON Writing", "File created successfully")
            else:
                results.fail_test("JSON Writing", "File not created")
                return

            # Read JSON
            loaded_data = file_manager.read_json_file(json_file)
            if loaded_data == test_data:
                results.pass_test("JSON Reading", "Data matches original")
            else:
                results.fail_test("JSON Reading", "Data mismatch")

            # Test file info
            file_info = file_manager.get_file_info(json_file)
            if 'size_bytes' in file_info and 'created' in file_info:
                results.pass_test("File Info", "Metadata extracted successfully")
            else:
                results.fail_test("File Info", "Missing metadata")

    except Exception as e:
        results.fail_test("File Utilities", f"Error: {e}", e)


def test_text_utils(results: TestResults) -> None:
    """Test text processing utilities."""
    print("\n" + "="*60)
    print("Testing Text Utilities")
    print("="*60)

    try:
        text_processor = TextProcessor()

        # Test text cleaning
        dirty_text = "  This is   messy\n\n\ntext  with   extra   spaces  "
        clean_text = text_processor.clean_text(dirty_text)
        if "extra" in clean_text and clean_text.strip() == clean_text:
            results.pass_test("Text Cleaning", "Text cleaned successfully")
        else:
            results.fail_test("Text Cleaning", "Text not cleaned properly")

        # Test section header detection
        header_text = "INTRODUCTION"
        if text_processor.is_section_header(header_text, "header"):
            results.pass_test("Header Detection", "Section header detected")
        else:
            results.fail_test("Header Detection", "Failed to detect section header")

        # Test sentence extraction
        paragraph = "This is sentence one. This is sentence two! And this is sentence three?"
        sentences = text_processor.extract_sentences(paragraph)
        if len(sentences) >= 2:  # Should extract multiple sentences
            results.pass_test("Sentence Extraction", f"Extracted {len(sentences)} sentences")
        else:
            results.fail_test("Sentence Extraction", "Failed to extract sentences")

        # Test text statistics
        stats = text_processor.get_text_statistics("Hello world! This is a test.")
        if stats['words'] > 0 and stats['characters'] > 0:
            results.pass_test("Text Statistics", f"Words: {stats['words']}, Chars: {stats['characters']}")
        else:
            results.fail_test("Text Statistics", "Failed to generate statistics")

    except Exception as e:
        results.fail_test("Text Utilities", f"Error: {e}", e)


def test_pdf_processor(results: TestResults, pdf_path: Optional[str] = None) -> Optional[Dict]:
    """Test PDF processing functionality."""
    print("\n" + "="*60)
    print("Testing PDF Processor")
    print("="*60)

    if not pdf_path or not Path(pdf_path).exists():
        results.skip_test("PDF Processing", "No PDF file available for testing")
        return None

    try:
        processor = PDFProcessor()

        # Test PDF processing
        start_time = time.time()
        doc = processor.process_pdf(pdf_path)
        process_time = time.time() - start_time

        if doc:
            results.pass_test("PDF Processing", f"Completed in {process_time:.2f}s")
        else:
            results.fail_test("PDF Processing", "Failed to process PDF")
            return None

        # Test structure extraction
        start_time = time.time()
        structured_data = processor.extract_structured_data(doc)
        extract_time = time.time() - start_time

        if structured_data and 'content' in structured_data:
            content_count = len(structured_data.get('content', []))
            table_count = len(structured_data.get('tables', []))
            image_count = len(structured_data.get('images', []))
            ref_count = len(structured_data.get('references', []))

            results.pass_test("Structure Extraction",
                            f"Extracted in {extract_time:.2f}s - Content: {content_count}, "
                            f"Tables: {table_count}, Images: {image_count}, Refs: {ref_count}")

            # Test section summary
            section_summary = processor.get_section_summary(structured_data)
            if section_summary:
                results.pass_test("Section Summary", f"Generated summary for {len(section_summary)} sections")
            else:
                results.warn("Section Summary generation returned empty result")

            return structured_data
        else:
            results.fail_test("Structure Extraction", "Failed to extract structure")
            return None

    except Exception as e:
        results.fail_test("PDF Processor", f"Error: {e}", e)
        return None


def test_html_generator(results: TestResults, structured_data: Optional[Dict] = None) -> None:
    """Test HTML generation functionality."""
    print("\n" + "="*60)
    print("Testing HTML Generator")
    print("="*60)

    if not structured_data:
        # Create minimal test data
        structured_data = {
            'metadata': {'total_items': 3, 'processing_timestamp': '2024-01-01T00:00:00'},
            'content': [
                {'type': 'text', 'text': 'This is a test paragraph.'},
                {'type': 'header', 'text': 'Test Section'}
            ],
            'tables': [],
            'images': [],
            'references': []
        }

    try:
        generator = HTMLGenerator()

        # Test HTML generation
        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = Path(temp_dir) / "test_output.html"

            start_time = time.time()
            generator.generate(structured_data, str(html_file), "Test Document")
            generate_time = time.time() - start_time

            if html_file.exists():
                file_size = html_file.stat().st_size
                results.pass_test("HTML Generation",
                                f"Generated in {generate_time:.2f}s, Size: {file_size} bytes")

                # Check HTML content
                html_content = html_file.read_text(encoding='utf-8')

                # Test for essential HTML elements
                checks = [
                    ('HTML Structure', '<html' in html_content and '</html>' in html_content),
                    ('CSS Styles', '<style>' in html_content or 'style>' in html_content),
                    ('Title', 'Test Document' in html_content),
                    ('Content', 'test paragraph' in html_content.lower()),
                ]

                for check_name, condition in checks:
                    if condition:
                        results.pass_test(f"HTML {check_name}", "Present in output")
                    else:
                        results.fail_test(f"HTML {check_name}", "Missing from output")

            else:
                results.fail_test("HTML Generation", "Output file not created")

        # Test markdown table conversion
        table_text = "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |"
        html_table = generator.convert_markdown_table_to_html(table_text)
        if '<table' in html_table and '<th>' in html_table:
            results.pass_test("Markdown Table Conversion", "Table converted successfully")
        else:
            results.fail_test("Markdown Table Conversion", "Failed to convert table")

        # Test base64 image detection
        base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        data_url, is_image = generator.detect_and_convert_base64_image(base64_data)
        if is_image and 'data:image/' in data_url:
            results.pass_test("Base64 Image Detection", "Image detected and converted")
        else:
            results.fail_test("Base64 Image Detection", "Failed to detect/convert image")

    except Exception as e:
        results.fail_test("HTML Generator", f"Error: {e}", e)


def test_cli_validation(results: TestResults) -> None:
    """Test CLI validation functionality."""
    print("\n" + "="*60)
    print("Testing CLI Validation")
    print("="*60)

    try:
        # Import CLI class
        sys.path.insert(0, str(Path(__file__).parent))
        from main import ChunkMonkeyCLI

        cli = ChunkMonkeyCLI()

        # Test validation
        is_valid = cli.validate_installation()
        if is_valid:
            results.pass_test("CLI Validation", "Installation validation passed")
        else:
            results.fail_test("CLI Validation", "Installation validation failed")

    except ImportError as e:
        results.fail_test("CLI Import", f"Failed to import CLI: {e}")
    except Exception as e:
        results.fail_test("CLI Validation", f"Error: {e}", e)


def test_end_to_end_pipeline(results: TestResults, pdf_path: Optional[str] = None) -> None:
    """Test complete end-to-end pipeline."""
    print("\n" + "="*60)
    print("Testing End-to-End Pipeline")
    print("="*60)

    if not pdf_path or not Path(pdf_path).exists():
        results.skip_test("End-to-End Pipeline", "No PDF file available")
        return

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            # Import CLI
            sys.path.insert(0, str(Path(__file__).parent))
            from main import ChunkMonkeyCLI

            cli = ChunkMonkeyCLI()

            # Run full pipeline
            start_time = time.time()
            result = cli.process_pdf_full_pipeline(
                pdf_path,
                str(output_dir),
                "test_document"
            )
            pipeline_time = time.time() - start_time

            if result and 'structured_json' in result:
                results.pass_test("Full Pipeline", f"Completed in {pipeline_time:.2f}s")

                # Check output files
                expected_files = ['structured_json', 'section_summary', 'html_output']
                for file_type in expected_files:
                    if file_type in result and Path(result[file_type]).exists():
                        file_size = Path(result[file_type]).stat().st_size
                        results.pass_test(f"Pipeline Output: {file_type}", f"Created ({file_size} bytes)")
                    else:
                        results.fail_test(f"Pipeline Output: {file_type}", "File not created")

            else:
                results.fail_test("Full Pipeline", "Pipeline failed to complete")

    except Exception as e:
        results.fail_test("End-to-End Pipeline", f"Error: {e}", e)


def main():
    """Main test function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test Chunk Monkey Implementation")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--create-sample', action='store_true', help='Create sample PDF for testing')
    parser.add_argument('--pdf', help='Path to PDF file for testing')
    parser.add_argument('--skip-pdf', action='store_true', help='Skip PDF-related tests')

    args = parser.parse_args()

    print("🐒 Chunk Monkey Implementation Test Suite")
    print("=" * 60)
    print("Testing the new modular implementation...")
    print()

    results = TestResults()

    # Determine PDF file for testing
    pdf_path = None
    if not args.skip_pdf:
        if args.pdf:
            pdf_path = args.pdf
        elif Path("burns.pdf").exists():
            pdf_path = "burns.pdf"
        elif args.create_sample:
            sample_path = "test_sample.pdf"
            if create_sample_pdf(sample_path):
                pdf_path = sample_path
                print(f"✅ Created sample PDF: {sample_path}")
            else:
                print("⚠️  Could not create sample PDF (reportlab not available)")

    # Run tests
    test_imports(results)
    test_configuration(results)
    test_file_utils(results)
    test_text_utils(results)

    # PDF-dependent tests
    structured_data = test_pdf_processor(results, pdf_path)
    test_html_generator(results, structured_data)

    # CLI tests
    test_cli_validation(results)
    test_end_to_end_pipeline(results, pdf_path)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    summary = results.summary()

    print(f"Total Tests: {summary['total']}")
    print(f"✅ Passed: {summary['passed']}")
    print(f"❌ Failed: {summary['failed']}")
    print(f"⏭️  Skipped: {summary['skipped']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")

    if summary['warnings']:
        print(f"\n⚠️  Warnings ({len(summary['warnings'])}):")
        for warning in summary['warnings']:
            print(f"   {warning}")

    if summary['errors']:
        print(f"\n❌ Errors ({len(summary['errors'])}):")
        for error in summary['errors']:
            print(f"   {error}")

    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")

    if summary['failed'] == 0:
        print("🎉 All tests passed! The implementation is working correctly.")
        print("   You can now use Chunk Monkey with confidence.")
        if pdf_path:
            print(f"   Try: uv run python main.py process {pdf_path}")
        else:
            print("   Try: uv run python main.py process your_document.pdf")
    else:
        print("🔧 Some tests failed. Please address the issues above.")
        print("   Check the error messages and fix any configuration or dependency issues.")

    if summary['skipped'] > 0:
        print(f"ℹ️  {summary['skipped']} tests were skipped.")
        if not pdf_path:
            print("   Place a PDF file in the directory or use --create-sample to test PDF processing.")

    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    print("1. If tests passed, try the CLI: uv run python main.py validate")
    print("2. Process a document: uv run python main.py process your_file.pdf")
    print("3. Run examples: uv run python examples/basic_usage.py")
    print("4. Read the documentation in README.md")

    # Clean up sample file if created
    if args.create_sample and Path("test_sample.pdf").exists():
        try:
            Path("test_sample.pdf").unlink()
            print("\n🧹 Cleaned up sample PDF file")
        except:
            pass

    # Exit with appropriate code
    sys.exit(0 if summary['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
