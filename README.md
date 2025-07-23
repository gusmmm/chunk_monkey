# Chunk Monkey 🐒

A clean, professional PDF processing pipeline that converts PDF documents into structured JSON and beautiful HTML visualizations.

## Overview

Chunk Monkey is a comprehensive tool for processing PDF documents with a focus on:
- **Complete Document Extraction** - PDFs to Markdown, JSON, and HTML
- **Image Extraction** - Save tables and figures as separate PNG files
- **Multiple Output Formats** - Markdown (embedded/referenced), JSON, HTML
- **Professional HTML** - Beautiful, responsive visualizations with proper image/table rendering
- **Simple CLI** - Easy-to-use command-line interface
- **Modular Design** - Clean, maintainable codebase

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for fast Python package management.

```bash
# Clone the repository
git clone <repository-url>
cd chunk_monkey

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## Quick Start

### Process a PDF (Enhanced Pipeline)
```bash
uv run python main.py process your_document.pdf
```

This will:
1. **Extract images** - Save tables and figures as separate PNG files
2. **Generate Markdown** - Create markdown files with embedded/referenced images
3. **Create structured JSON** - For AI/LLM processing
4. **Generate HTML** - Beautiful visualization with proper image/table rendering
5. **Display all output paths** - Easy access to generated files

### Individual Steps

**PDF to JSON only:**
```bash
uv run python main.py json your_document.pdf
```

**JSON to HTML only:**
```bash
uv run python main.py html structured_data.json
```

**Batch process multiple PDFs:**
```bash
uv run python main.py batch /path/to/pdf/directory/
```

### Options

- `-v, --verbose` - Enable detailed logging
- `-o, --output DIR` - Specify output directory (default: `./output`)

## Project Structure

```
chunk_monkey/
├── src/                    # Core implementation
│   ├── processors/         # PDF processing with image extraction
│   ├── generators/         # HTML generation with image support
│   ├── config/            # Configuration settings
│   └── utils/             # Utility functions
├── examples/              # Usage examples
├── test-data/             # Test PDF files
├── output/                # Generated outputs (images, markdown, JSON, HTML)
├── legacy/                # Old files and examples
├── main.py               # CLI entry point
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Example Usage

### Programmatic Usage

```python
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from processors.pdf_processor import PDFProcessor
from generators.html_generator import HTMLGenerator
from utils.file_utils import FileManager

# Initialize components
pdf_processor = PDFProcessor()
html_generator = HTMLGenerator()
file_manager = FileManager()

# Enhanced processing with image extraction
pdf_path = Path("document.pdf")
results = pdf_processor.process_complete_pipeline(str(pdf_path), "output")

# Results contains paths to all generated files:
# - Markdown with embedded images
# - Markdown with image references  
# - Individual PNG files for tables/figures
# - Structured JSON data
# - Docling-generated HTML
# - Custom HTML visualization

print("Generated files:", results)
```

### Run the Example

```bash
cd examples
uv run python basic_usage.py
```

## Features

- **Enhanced PDF Processing**: Complete extraction using Docling with image support
- **Image Extraction**: Automatic extraction of tables and figures as PNG files
- **Multiple Markdown Formats**: Embedded images (base64) and referenced images
- **Structured JSON**: Clean format suitable for AI/LLM processing
- **Professional HTML**: Responsive visualization with proper image/table rendering
- **Batch Processing**: Handle multiple PDFs efficiently
- **Error Handling**: Robust error reporting and logging
- **Modular Design**: Easy to extend and customize

## Output Formats

### Complete Output Structure
When processing a PDF, you get:

**Images** (PNG files):
- `document-table-1.png`, `document-table-2.png` - Extracted table images
- `document-picture-1.png`, `document-picture-2.png` - Extracted figure images

**Markdown Files**:
- `document-with-images.md` - Markdown with embedded base64 images
- `document-with-image-refs.md` - Markdown with image file references
- `document.md` - Simple markdown for compatibility

**JSON Structure**:
```json
{
  "metadata": {
    "title": "Document Title",
    "pages": 10,
    "processed_at": "2024-01-01T12:00:00"
  },
  "content": [
    {
      "type": "heading",
      "text": "Section Title",
      "level": 1
    },
    {
      "type": "paragraph", 
      "text": "Content text..."
    }
  ],
  "tables": [...],
  "images": [...]
}
```

**HTML Files**:
- `document-docling.html` - Docling's native HTML with image references
- `document_output.html` - Custom responsive HTML visualization

### HTML Features
- Responsive design with proper image/table rendering
- Interactive navigation and table of contents
- Search functionality and filtering
- Print-friendly styling
- External image references for faster loading

## Dependencies

- **docling** - PDF processing and extraction
- **rich** - Enhanced terminal output
- **python-dotenv** - Environment variable management

## Development

The codebase is organized into clear modules:

- `src/processors/` - PDF processing logic
- `src/generators/` - HTML generation
- `src/config/` - Configuration management
- `src/utils/` - Shared utilities

To add new functionality, extend the appropriate module and update the CLI in `main.py`.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the `examples/` directory for usage patterns
- Review the `legacy/` directory for additional examples
- Open an issue on the repository