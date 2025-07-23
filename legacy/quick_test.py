#!/usr/bin/env python3
"""
Quick Test for Chunk Monkey
===========================

A simple test script to verify the basic functionality of the Chunk Monkey
implementation without requiring external PDFs or complex dependencies.

Usage:
    uv run python quick_test.py

This script tests:
- Module imports
- Configuration loading
- Basic utility functions
- Mock data processing
- HTML generation with sample data

Author: Chunk Monkey Team
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing module imports...")

    try:
        from processors.pdf_processor import PDFProcessor
        print("  ✅ PDFProcessor imported")
    except ImportError as e:
        print(f"  ❌ PDFProcessor import failed: {e}")
        return False

    try:
        from generators.html_generator import HTMLGenerator
        print("  ✅ HTMLGenerator imported")
    except ImportError as e:
        print(f"  ❌ HTMLGenerator import failed: {e}")
        return False

    try:
        from utils.file_utils import FileManager
        print("  ✅ FileManager imported")
    except ImportError as e:
        print(f"  ❌ FileManager import failed: {e}")
        return False

    try:
        from utils.text_utils import TextProcessor
        print("  ✅ TextProcessor imported")
    except ImportError as e:
        print(f"  ❌ TextProcessor import failed: {e}")
        return False

    try:
        from config.settings import get_config
        print("  ✅ Configuration imported")
    except ImportError as e:
        print(f"  ❌ Configuration import failed: {e}")
        return False

    return True

def test_configuration():
    """Test configuration system."""
    print("\n🔧 Testing configuration...")

    try:
        from config.settings import get_config, validate_config

        config = get_config()
        print("  ✅ Configuration loaded")

        # Check for key sections
        required = ['pdf_processing', 'json', 'html', 'logging']
        for section in required:
            if section in config:
                print(f"  ✅ {section} section present")
            else:
                print(f"  ❌ {section} section missing")
                return False

        # Test validation
        if validate_config():
            print("  ✅ Configuration validation passed")
        else:
            print("  ⚠️  Configuration validation failed")

        return True

    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_text_utilities():
    """Test text processing utilities."""
    print("\n📝 Testing text utilities...")

    try:
        from utils.text_utils import TextProcessor

        processor = TextProcessor()

        # Test text cleaning
        dirty_text = "  This   is   messy    text  "
        clean_text = processor.clean_text(dirty_text)
        if clean_text == "This is messy text":
            print("  ✅ Text cleaning works")
        else:
            print(f"  ❌ Text cleaning failed: '{clean_text}'")
            return False

        # Test header detection
        if processor.is_section_header("INTRODUCTION", "header"):
            print("  ✅ Header detection works")
        else:
            print("  ❌ Header detection failed")
            return False

        # Test sentence extraction
        text = "First sentence. Second sentence! Third sentence?"
        sentences = processor.extract_sentences(text)
        if len(sentences) >= 2:
            print(f"  ✅ Sentence extraction works ({len(sentences)} sentences)")
        else:
            print("  ❌ Sentence extraction failed")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Text utilities test failed: {e}")
        return False

def test_file_utilities():
    """Test file management utilities."""
    print("\n📁 Testing file utilities...")

    try:
        from utils.file_utils import FileManager
        import tempfile
        import json

        manager = FileManager()

        # Test with temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test directory creation
            test_dir = temp_path / "test_subdir"
            created = manager.ensure_directory(test_dir)
            if created.exists():
                print("  ✅ Directory creation works")
            else:
                print("  ❌ Directory creation failed")
                return False

            # Test JSON operations
            test_data = {"test": "value", "number": 42}
            json_file = test_dir / "test.json"

            manager.write_json_file(json_file, test_data)
            if json_file.exists():
                print("  ✅ JSON writing works")
            else:
                print("  ❌ JSON writing failed")
                return False

            loaded_data = manager.read_json_file(json_file)
            if loaded_data == test_data:
                print("  ✅ JSON reading works")
            else:
                print("  ❌ JSON reading failed")
                return False

        return True

    except Exception as e:
        print(f"  ❌ File utilities test failed: {e}")
        return False

def test_html_generation():
    """Test HTML generation with sample data."""
    print("\n🌐 Testing HTML generation...")

    try:
        from generators.html_generator import HTMLGenerator
        import tempfile

        generator = HTMLGenerator()

        # Create sample structured data
        sample_data = {
            "metadata": {
                "total_items": 5,
                "processing_timestamp": "2024-01-15T10:30:00"
            },
            "content": [
                {
                    "type": "header",
                    "text": "Sample Document",
                    "section_hierarchy": ["Sample Document"],
                    "parent_section": None,
                    "subsection": None
                },
                {
                    "type": "text",
                    "text": "This is a sample paragraph to test the HTML generation functionality.",
                    "section_hierarchy": ["Sample Document"],
                    "parent_section": "Sample Document",
                    "subsection": None
                },
                {
                    "type": "header",
                    "text": "Introduction",
                    "section_hierarchy": ["Introduction"],
                    "parent_section": None,
                    "subsection": None
                },
                {
                    "type": "text",
                    "text": "This section contains introductory material with **bold text** and *italic text*.",
                    "section_hierarchy": ["Introduction"],
                    "parent_section": "Introduction",
                    "subsection": None
                }
            ],
            "tables": [
                {
                    "content": "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |\n| Cell 3   | Cell 4   |",
                    "caption": "Sample Table",
                    "item_type": "table",
                    "label": "table_1",
                    "section_hierarchy": ["Introduction"],
                    "parent_section": "Introduction",
                    "subsection": None
                }
            ],
            "images": [],
            "references": [
                {
                    "type": "reference",
                    "text": "1. Sample Reference Author. (2024). Sample Paper Title. Journal Name.",
                    "section_hierarchy": ["References"],
                    "parent_section": "References",
                    "subsection": None
                }
            ]
        }

        # Test HTML generation
        with tempfile.TemporaryDirectory() as temp_dir:
            html_file = Path(temp_dir) / "test_output.html"

            generator.generate(sample_data, str(html_file), "Test Document")

            if html_file.exists():
                print("  ✅ HTML file created")
            else:
                print("  ❌ HTML file not created")
                return False

            # Check HTML content
            html_content = html_file.read_text(encoding='utf-8')

            checks = [
                ("HTML structure", "<html" in html_content and "</html>" in html_content),
                ("Title", "Test Document" in html_content),
                ("CSS styles", "<style>" in html_content),
                ("Sample content", "sample paragraph" in html_content.lower()),
                ("Table conversion", "<table" in html_content and "<th>" in html_content),
                ("Bold formatting", "<strong>" in html_content),
                ("Italic formatting", "<em>" in html_content)
            ]

            all_passed = True
            for check_name, passed in checks:
                if passed:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    all_passed = False

            if all_passed:
                file_size = html_file.stat().st_size
                print(f"  ✅ HTML generation complete ({file_size} bytes)")

            return all_passed

    except Exception as e:
        print(f"  ❌ HTML generation test failed: {e}")
        return False

def test_cli_availability():
    """Test that CLI is available."""
    print("\n⌨️  Testing CLI availability...")

    try:
        # Check if main.py exists
        main_file = Path(__file__).parent / "main.py"
        if main_file.exists():
            print("  ✅ main.py exists")
        else:
            print("  ❌ main.py not found")
            return False

        # Try to import CLI class
        sys.path.insert(0, str(Path(__file__).parent))
        from main import ChunkMonkeyCLI
        print("  ✅ CLI class imported")

        # Test CLI initialization
        cli = ChunkMonkeyCLI()
        print("  ✅ CLI initialized")

        return True

    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False

def main():
    """Run all quick tests."""
    print("🐒 Chunk Monkey Quick Test")
    print("=" * 50)
    print("Testing basic functionality without external dependencies...\n")

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Text Utilities", test_text_utilities),
        ("File Utilities", test_file_utilities),
        ("HTML Generation", test_html_generation),
        ("CLI Availability", test_cli_availability),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ⚠️  {test_name} had some failures")
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")

    # Summary
    print("\n" + "=" * 50)
    print("QUICK TEST SUMMARY")
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 All basic tests passed!")
        print("The Chunk Monkey implementation appears to be working correctly.")
        print("\nNext steps:")
        print("  1. Run: uv run python main.py validate")
        print("  2. Try: uv run python main.py process your_document.pdf")
        print("  3. Run: uv run python examples/basic_usage.py")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed!")
        print("The implementation is mostly working. Check any failed tests above.")
        print("\nYou can likely proceed with:")
        print("  uv run python main.py validate")
    else:
        print("\n❌ Several tests failed.")
        print("Please check the error messages above and fix any issues.")
        print("You may need to:")
        print("  1. Run 'uv sync' to install dependencies")
        print("  2. Check that you're in the chunk_monkey directory")
        print("  3. Verify all files are present")

    print(f"\nFor comprehensive testing with PDF files, run:")
    print("  uv run python test_implementation.py")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
