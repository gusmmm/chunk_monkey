#!/usr/bin/env python3
"""
Basic Usage Example for Chunk Monkey

A simple demonstration of how to use the Chunk Monkey PDF processing pipeline.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from processors.pdf_processor import PDFProcessor
from generators.html_generator import HTMLGenerator
from utils.file_utils import FileManager


def main():
    """Demonstrate basic PDF processing workflow."""
    print("🐒 Chunk Monkey - Basic Usage Example")
    print("=" * 50)

    # Check for test PDF
    pdf_path = Path("test-data/burns.pdf")
    if not pdf_path.exists():
        print("❌ Test PDF not found at:", pdf_path)
        print("Please ensure burns.pdf exists in the test-data directory")
        return

    # Initialize components
    pdf_processor = PDFProcessor()
    html_generator = HTMLGenerator()
    file_manager = FileManager()

    # Create output directory
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)

    try:
        # Step 1: Enhanced PDF processing with images and markdown
        print(f"📄 Processing PDF with image extraction: {pdf_path}")
        results = pdf_processor.process_complete_pipeline(str(pdf_path), str(output_dir))
        print("✅ PDF processed successfully with images extracted!")

        # Show all generated files
        print("\n📁 Generated Files:")
        for key, value in results.items():
            if key == 'output_directory':
                print(f"   📂 Output directory: {value}")
            elif key == 'images_extracted':
                print(f"   🖼️  Images extracted: {value}")
            elif 'markdown' in key:
                print(f"   📝 {key.replace('_', ' ').title()}: {Path(value).name}")
            elif 'html' in key:
                print(f"   🌐 {key.replace('_', ' ').title()}: {Path(value).name}")
            elif 'json' in key:
                print(f"   💾 {key.replace('_', ' ').title()}: {Path(value).name}")

        # Step 2: Load structured data for summary
        json_path = Path(results['json_structured'])
        structured_data = file_manager.read_json_file(json_path)

        # Summary
        content_items = len(structured_data.get('content', []))
        tables = len(structured_data.get('tables', []))
        images = len(structured_data.get('images', []))

        print("\n📊 Processing Summary:")
        print(f"   Content items: {content_items}")
        print(f"   Tables: {tables}")
        print(f"   Images: {images}")

        print("\n🎉 Enhanced processing completed successfully!")
        print(f"📂 Check output directory: {output_dir}")
        print(f"🌐 Open HTML files in your browser to view results")
        print(f"📝 Markdown files can be used with AI/LLM tools")

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
