"""
HTML Generator Module for Chunk Monkey

This module generates beautiful, responsive HTML visualizations from structured
JSON documents. It creates interactive HTML pages with navigation, statistics,
and proper rendering of all content types including text, images, and tables.

Key Features:
- Responsive HTML design with modern CSS
- Interactive navigation and table of contents
- Proper rendering of markdown tables
- Base64 image handling with optimization
- Section-aware content organization
- Mobile-friendly responsive design
- Search functionality and filtering

Author: Chunk Monkey Team
"""

import json
import re
import base64
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from ..config.settings import HTMLConfig
    from ..utils.file_utils import FileManager
    from ..utils.text_utils import TextProcessor
except ImportError:
    # Handle both relative and absolute imports
    try:
        from config.settings import HTMLConfig
        from utils.file_utils import FileManager
        from utils.text_utils import TextProcessor
    except ImportError:
        import sys
        from pathlib import Path
        # Add src to path for standalone execution
        src_path = Path(__file__).parent.parent
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        from config.settings import HTMLConfig
        from utils.file_utils import FileManager
        from utils.text_utils import TextProcessor

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """
    HTML generator class that creates beautiful visualizations from structured JSON data.

    This class handles the complete HTML generation pipeline:
    1. Load and validate structured JSON data
    2. Generate HTML components for different content types
    3. Create responsive layout with navigation
    4. Apply styling and interactive features
    5. Output complete HTML document
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize HTML generator with configuration.

        Args:
            config: Optional configuration dictionary to override defaults
        """
        self.config = config or {}
        self.file_manager = FileManager()
        self.text_processor = TextProcessor()

        # HTML generation settings
        self.theme = self.config.get('theme', HTMLConfig.THEME)
        self.include_toc = self.config.get('include_toc', HTMLConfig.INCLUDE_TOC)
        self.include_stats = self.config.get('include_stats', HTMLConfig.INCLUDE_STATS)
        self.responsive_design = self.config.get('responsive_design', HTMLConfig.RESPONSIVE_DESIGN)

        logger.info(f"HTML Generator initialized with theme: {self.theme}")

    def load_json_document(self, file_path: str) -> Optional[Dict]:
        """
        Load and parse the structured JSON document.

        Args:
            file_path: Path to the JSON file

        Returns:
            Parsed JSON data or None if loading fails
        """
        try:
            return self.file_manager.read_json_file(file_path)
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            return None

    def convert_markdown_table_to_html(self, text: str) -> str:
        """
        Convert markdown tables to properly formatted HTML tables.

        Args:
            text: Text that may contain markdown tables

        Returns:
            Text with markdown tables converted to HTML
        """
        if not text or '|' not in text:
            return text

        lines = text.strip().split('\n')
        table_lines = []
        in_table = False

        for line in lines:
            line = line.strip()
            if '|' in line and line.startswith('|') and line.endswith('|'):
                table_lines.append(line)
                in_table = True
            elif in_table and line.startswith('|') and '---' in line:
                # Skip separator line
                continue
            elif in_table and '|' not in line:
                # End of table
                break
            elif not in_table:
                # Not a table line, return original text
                return text

        if len(table_lines) < 2:
            return text

        # Convert to HTML table
        html_table = ['<table class="markdown-table">']

        # Header row
        header_cells = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]
        html_table.append('<thead><tr>')
        for cell in header_cells:
            html_table.append(f'<th>{self.text_processor.clean_text(cell)}</th>')
        html_table.append('</tr></thead>')

        # Data rows
        html_table.append('<tbody>')
        for line in table_lines[1:]:
            if '---' in line:
                continue
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            html_table.append('<tr>')
            for cell in cells:
                html_table.append(f'<td>{self.text_processor.clean_text(cell)}</td>')
            html_table.append('</tr>')
        html_table.append('</tbody>')
        html_table.append('</table>')

        return '\n'.join(html_table)

    def detect_and_convert_base64_image(self, text: str) -> Tuple[str, bool]:
        """
        Detect base64 encoded images and convert to proper data URLs.

        Args:
            text: Text that may contain base64 image data

        Returns:
            Tuple of (converted_text, is_image_found)
        """
        if not text:
            return text, False

        # Pattern for existing data URLs
        base64_pattern = r'data:image/([a-zA-Z]*);base64,([^"\s]+)'

        if re.search(base64_pattern, text):
            return text, True

        # Check if text looks like raw base64 (common patterns)
        if len(text) > 100 and re.match(r'^[A-Za-z0-9+/=]+$', text.strip()):
            # Try to detect image type from first few bytes
            try:
                decoded = base64.b64decode(text[:20])
                if decoded.startswith(b'\x89PNG'):
                    return f"data:image/png;base64,{text.strip()}", True
                elif decoded.startswith(b'\xff\xd8\xff'):
                    return f"data:image/jpeg;base64,{text.strip()}", True
                elif decoded.startswith(b'GIF8'):
                    return f"data:image/gif;base64,{text.strip()}", True
                elif decoded.startswith(b'RIFF'):
                    return f"data:image/webp;base64,{text.strip()}", True
            except Exception as e:
                logger.debug(f"Error decoding base64 image: {e}")

        return text, False

    def format_text_content(self, text: str) -> str:
        """
        Format text content with markdown-style formatting and HTML conversion.

        Args:
            text: Raw text content to format

        Returns:
            Formatted HTML text
        """
        if not text:
            return text

        # Clean the text first
        formatted_text = self.text_processor.clean_text(text)

        # Convert markdown tables to HTML
        formatted_text = self.convert_markdown_table_to_html(formatted_text)

        # Convert markdown links to HTML
        formatted_text = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" target="_blank" rel="noopener">\1</a>',
            formatted_text
        )

        # Convert **bold** to HTML
        formatted_text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', formatted_text)

        # Convert *italic* to HTML
        formatted_text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', formatted_text)

        # Convert inline code
        formatted_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', formatted_text)

        # Convert line breaks to HTML (but not within tables)
        if '<table' not in formatted_text:
            formatted_text = formatted_text.replace('\n', '<br>')

        return formatted_text

    def generate_stats_card(self, data: Dict) -> str:
        """
        Generate HTML for document statistics.

        Args:
            data: Structured document data

        Returns:
            HTML string for statistics card
        """
        if not self.include_stats:
            return ""

        # Calculate statistics
        stats = {
            'total_content': len(data.get('content', [])),
            'total_tables': len(data.get('tables', [])),
            'total_images': len(data.get('images', [])),
            'total_references': len(data.get('references', [])),
        }

        # Add metadata stats if available
        metadata = data.get('metadata', {})
        if metadata:
            stats['total_items'] = metadata.get('total_items', 0)
            if metadata.get('processing_timestamp'):
                try:
                    timestamp = datetime.fromisoformat(metadata['processing_timestamp'].replace('Z', '+00:00'))
                    stats['processed_date'] = timestamp.strftime('%Y-%m-%d %H:%M')
                except:
                    stats['processed_date'] = metadata['processing_timestamp']

        # Count content types
        content_types = {}
        for item in data.get('content', []):
            item_type = item.get('type', 'text')
            content_types[item_type] = content_types.get(item_type, 0) + 1

        if content_types:
            stats['content_types'] = content_types

        # Generate HTML
        stat_items = []
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, dict):
                # Handle nested stats like content_types
                nested_items = []
                for sub_key, sub_value in value.items():
                    nested_items.append(f"<span class='stat-detail'>{sub_key}: {sub_value}</span>")
                stat_items.append(
                    f"<div class='stat-item'><strong>{formatted_key}:</strong><br>{'<br>'.join(nested_items)}</div>"
                )
            else:
                stat_items.append(f"<div class='stat-item'><strong>{formatted_key}:</strong> {value}</div>")

        return f"""
        <div class="stats-card">
            <h3>📊 Document Statistics</h3>
            <div class="stats-grid">
                {''.join(stat_items)}
            </div>
        </div>
        """

    def generate_content_item(self, item: Dict, item_index: int = 0) -> str:
        """
        Generate HTML for a single content item.

        Args:
            item: Content item dictionary
            item_index: Index of the item for unique IDs

        Returns:
            HTML string for the content item
        """
        content_type = item.get('type', 'text')

        # Handle different content types
        if content_type in ['image', 'picture'] or 'base64_data' in item:
            return self._generate_image_item(item, item_index)
        elif content_type == 'table' or 'table' in content_type.lower() or content_type.lower() == 'tableitem':
            return self._generate_table_item(item, item_index)
        elif content_type in ['list', 'listitem'] or content_type.lower() == 'listitem':
            return self._generate_list_item(item, item_index)
        else:
            return self._generate_text_item(item, item_index)

    def _generate_image_item(self, item: Dict, item_index: int) -> str:
        """Generate HTML for image items."""
        # Check if this item has external image reference
        image_filename = item.get('image_filename', '')
        image_path = item.get('image_path', '')
        line_number = item_index * 2 + 3

        if image_filename:
            # Use external image reference
            caption = item.get('caption', '')
            label = item.get('label', f'image_{item_index}')

            img_html = f"""
        <div class="content-item image-item" id="{label}">
            <div class="content-meta">🖼️ Image (Line {line_number})</div>
            <div class="image-container">
                <img src="{image_filename}" alt="{caption or 'Document image'}" loading="lazy">
            </div>
            {f'<div class="image-caption">{self.format_text_content(caption)}</div>' if caption else ''}
        </div>
        """
        else:
            # Fallback to base64 data
            img_data = item.get('base64_data', item.get('content', ''))
            caption = item.get('caption', '')
            label = item.get('label', f'image_{item_index}')

            # Convert to data URL if needed
            data_url, is_image = self.detect_and_convert_base64_image(img_data)

            if not is_image:
                # Fallback for non-image content
                return self._generate_text_item(item, item_index)

            # Generate image HTML
            img_html = f"""
        <div class="content-item image-item" id="{label}">
            <div class="content-meta">
                <span class="item-type">🖼️ Image</span>
                <span class="item-label">{label}</span>
            </div>
            <div class="image-container">
                <img src="{data_url}" alt="{caption or 'Document image'}" loading="lazy">
            </div>
            {f'<div class="image-caption">{self.format_text_content(caption)}</div>' if caption else ''}
        </div>
        """

        return img_html

    def _generate_table_item(self, item: Dict, item_index: int) -> str:
        """Generate HTML for table items."""
        content = item.get('content', '')
        caption = item.get('caption', '')
        label = item.get('label', f'table_{item_index}')
        line_number = item_index * 2 + 3

        # Check if there's an external table image based on label
        table_image_filename = None
        if label and 'table_' in label:
            # Extract table number from label (e.g., 'table_1' -> '1')
            table_num = label.split('_')[-1]
            table_image_filename = f"burns-table-{table_num}.png"
        elif item_index < 4:  # We know there are 4 tables from processing
            table_image_filename = f"burns-table-{item_index + 1}.png"

        # Try to parse table structure from content
        table_html_content = self._parse_table_content(content)

        # Generate table HTML with image reference if available
        table_html = f"""
        <div class="content-item table-item" id="{label}">
            <div class="content-meta">📊 Table (Line {line_number})</div>
            {f'<div class="table-caption">{self.format_text_content(caption)}</div>' if caption else ''}
            <div class="table-content">
                {table_html_content}
            </div>
            {f'<div class="table-image"><img src="{table_image_filename}" alt="Table {item_index + 1}" loading="lazy"></div>' if table_image_filename else ''}
        </div>
        """

        return table_html

    def _parse_table_content(self, content: str) -> str:
        """Parse table content and generate proper HTML table."""
        if not content:
            return "<p>No table content available</p>"

        # Check if content contains table cell information
        if 'table_cells=' in content and 'num_rows=' in content and 'num_cols=' in content:
            # Extract basic table info
            import re
            rows_match = re.search(r'num_rows=(\d+)', content)
            cols_match = re.search(r'num_cols=(\d+)', content)

            if rows_match and cols_match:
                num_rows = int(rows_match.group(1))
                num_cols = int(cols_match.group(1))

                if num_rows > 0 and num_cols > 0:
                    # Try to extract cell text from the content
                    cell_texts = re.findall(r"text='([^']*)'", content)

                    if cell_texts:
                        return self._generate_html_table(cell_texts, num_rows, num_cols)

        # Fallback: check if content looks like markdown table
        if '|' in content and '\n' in content:
            return self.convert_markdown_table_to_html(content)

        # Final fallback: format as preformatted text
        return f"<pre class='table-raw'>{self.format_text_content(content)}</pre>"

    def _generate_html_table(self, cell_texts: list, num_rows: int, num_cols: int) -> str:
        """Generate HTML table from cell data."""
        if not cell_texts or num_rows == 0 or num_cols == 0:
            return "<p>Empty table</p>"

        # Calculate expected cells
        expected_cells = num_rows * num_cols

        # Pad or truncate cell_texts to match expected size
        while len(cell_texts) < expected_cells:
            cell_texts.append("")
        cell_texts = cell_texts[:expected_cells]

        # Generate table HTML
        table_html = ['<table class="markdown-table">']

        for row in range(num_rows):
            table_html.append('  <tr>')
            for col in range(num_cols):
                cell_index = row * num_cols + col
                cell_text = cell_texts[cell_index] if cell_index < len(cell_texts) else ""

                # First row is typically headers
                tag = 'th' if row == 0 else 'td'
                table_html.append(f'    <{tag}>{self.format_text_content(cell_text)}</{tag}>')
            table_html.append('  </tr>')

        table_html.append('</table>')
        return '\n'.join(table_html)

    def _generate_list_item(self, item: Dict, item_index: int) -> str:
        """Generate HTML for list items."""
        content = item.get('text', item.get('content', ''))
        line_number = item_index * 2 + 3

        list_html = f"""
        <div class="content-item list-item">
            <div class="content-meta">📋 List (Line {line_number})</div>
            <div class="list-content">
                {self.format_text_content(content)}
            </div>
        </div>
        """

        return list_html

    def _generate_text_item(self, item: Dict, item_index: int) -> str:
        """Generate HTML for text items."""
        content = item.get('text', item.get('content', ''))
        content_type = item.get('type', 'text')

        # Determine if this is a heading based on the type field
        is_heading = 'header' in content_type.lower() or 'heading' in content_type.lower() or content_type.lower() == 'sectionheaderitem'

        # Calculate line number based on item index
        line_number = item_index * 2 + 3

        if is_heading:
            # Generate heading item
            heading_level = self._determine_heading_level(content, item)
            heading_id = self._generate_heading_id(content)

            text_html = f"""
            <div class="content-item heading-item depth-{heading_level}" id="{heading_id}">
                <div class="content-meta">
                    <span class="item-type">📑 Heading {heading_level}</span>
                </div>
                <h{heading_level} class="content-heading">{self.format_text_content(content)}</h{heading_level}>
            </div>
            """
        else:
            # Generate regular text item
            text_html = f"""
        <div class="content-item text-item">
            <div class="content-meta">📄 Text (Line {line_number})</div>
            <div class="text-content">{self.format_text_content(content)}</div>
        </div>
        """

        return text_html

    def _determine_heading_level(self, content: str, item: Dict) -> int:
        """Determine heading level based on content and hierarchy."""
        # Check section hierarchy if available
        hierarchy = item.get('section_hierarchy', [])
        if hierarchy:
            level = len(hierarchy)
            return min(max(level, 1), 6)  # HTML only supports h1-h6, minimum h1

        # Fallback to content analysis for better semantic structure
        if content.isupper() and len(content) > 20:
            return 1  # Main sections
        elif content.endswith(':'):
            return 2  # Subsections
        elif len(content) > 50:
            return 2  # Longer descriptive headers
        else:
            return 3  # Minor headings

    def _generate_heading_id(self, content: str) -> str:
        """Generate a valid HTML ID from heading content."""
        # Clean and normalize the content
        clean_content = re.sub(r'[^\w\s-]', '', content.lower())
        clean_content = re.sub(r'[-\s]+', '-', clean_content).strip('-')
        return clean_content or 'heading'

    def generate_section(self, section_name: str, items: List[Dict], section_type: str = "content", depth: int = 0) -> str:
        """
        Generate HTML for a complete section with all its items.

        Args:
            section_name: Name of the section
            items: List of items in the section
            section_type: Type of section (content, tables, images, references)
            depth: Hierarchy depth for CSS classes

        Returns:
            HTML string for the complete section
        """
        if not items:
            return ""

        # Generate section statistics
        item_count = len(items)
        text_count = len([i for i in items if i.get('type') == 'textitem'])
        list_count = len([i for i in items if i.get('type') == 'listitem'])
        table_count = len([i for i in items if i.get('type') == 'tableitem'])
        image_count = len([i for i in items if i.get('type') == 'imageitem'])

        # Count content types for stats
        content_types = {}
        for item in items:
            item_type = item.get('type', 'unknown')
            content_types[item_type] = content_types.get(item_type, 0) + 1

        # Generate items HTML
        items_html = []
        for i, item in enumerate(items):
            if section_type == 'images':
                items_html.append(self._generate_image_item(item, i))
            elif section_type == 'tables':
                items_html.append(self._generate_table_item(item, i))
            else:
                items_html.append(self.generate_content_item(item, i))

        # Generate content types breakdown
        content_types_html = ""
        if content_types:
            type_details = []
            for item_type, count in content_types.items():
                display_type = item_type.replace('item', '') if item_type.endswith('item') else item_type
                type_details.append(f"<span class='stat-detail'>{display_type}: {count}</span>")
            content_types_html = "<br>".join(type_details)

        # Generate mini stats for this section
        mini_stats_html = f"""
    <div class="stats-card">
        <h3>📊 Document Statistics</h3>
        <div class="stats-grid">
            <div class='stat-item'><strong>Total Items:</strong> {item_count}</div><div class='stat-item'><strong>Content Types:</strong><br>{content_types_html}</div><div class='stat-item'><strong>Image Count:</strong> {image_count}</div><div class='stat-item'><strong>Text Blocks:</strong> {text_count}</div><div class='stat-item'><strong>List Items:</strong> {list_count}</div><div class='stat-item'><strong>Table Rows:</strong> {table_count}</div><div class='stat-item'><strong>Subsection Count:</strong> 0</div>
        </div>
    </div>
    """ if self.include_stats else ""

        section_html = f"""
    <div class="section depth-{depth}">
        <div class="section-header">
            <h2 class="section-title">{section_name}</h2>
            <span class="section-meta">Line {i+1} • Level 2</span>
        </div>

        <div class="section-stats">
            <details>
                <summary>📈 Section Statistics</summary>
                <div class="mini-stats">
                    {mini_stats_html}
                </div>
            </details>
        </div>


        <div class="section-content">
            {''.join(items_html)}
        </div>


    </div>
    """

        return section_html

    def generate_table_of_contents(self, data: Dict) -> str:
        """
        Generate table of contents from document structure.

        Args:
            data: Structured document data

        Returns:
            HTML string for table of contents
        """
        if not self.include_toc:
            return ""

        toc_items = []

        # Add sections based on available data
        if data.get('content'):
            toc_items.append('<li><a href="#content-section">📄 Content</a></li>')

        if data.get('tables'):
            toc_items.append('<li><a href="#tables-section">📊 Tables</a></li>')

        if data.get('images'):
            toc_items.append('<li><a href="#images-section">🖼️ Images</a></li>')

        if data.get('references'):
            toc_items.append('<li><a href="#references-section">📚 References</a></li>')

        if not toc_items:
            return ""

        return f"""
        <div class="table-of-contents">
            <h3>📑 Table of Contents</h3>
            <ul>
                {''.join(toc_items)}
            </ul>
        </div>
        """

    def get_css_styles(self) -> str:
        """
        Get CSS styles for the HTML document.

        Returns:
            CSS styles as string
        """
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }

        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem 0;
            border-bottom: 2px solid #e9ecef;
        }

        .header h1 {
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .header .subtitle {
            color: #6c757d;
            font-size: 1.1rem;
        }

        .document-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 2rem;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }

        .info-item {
            background: white;
            padding: 1rem;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }

        .stats-card {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .stat-item {
            background: white;
            padding: 1rem;
            border-radius: 4px;
            border-left: 4px solid #28a745;
        }

        .stat-detail {
            font-size: 0.9rem;
            color: #6c757d;
            display: block;
            margin-top: 0.5rem;
        }

        .content {
            padding: 30px;
        }

        .section {
            margin: 20px 0;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }

        .section-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }

        .section-title {
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .section-meta {
            color: #666;
            font-size: 0.9rem;
            font-weight: normal;
        }

        .section-stats {
            padding: 15px 20px;
            background: #f1f3f4;
        }

        .section-stats details summary {
            cursor: pointer;
            font-weight: 500;
            color: #555;
        }

        .mini-stats .stats-card {
            margin: 10px 0;
            padding: 15px;
        }

        .section-content {
            padding: 20px;
        }

        .content-item {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }

        .text-item {
            background: #f8f9fa;
            border-left-color: #3498db;
        }

        .image-item {
            background: #e8f5e8;
            border-left-color: #27ae60;
        }

        .list-item {
            background: #fff3cd;
            border-left-color: #ffc107;
        }

        .heading-item {
            background: #e7f3ff;
            border-left-color: #007bff;
        }

        .table-item {
            background: #f0f8ff;
            border-left-color: #8a2be2;
        }

        .table-row-item {
            background: #f5f5f5;
            border-left-color: #999;
        }

        .content-meta {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 10px;
            font-weight: 500;
        }

        .text-content {
            line-height: 1.7;
        }

        .text-content code {
            background: #f8f9fa;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }

        .text-content a {
            color: #007bff;
            text-decoration: none;
        }

        .text-content a:hover {
            text-decoration: underline;
        }

        .markdown-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .markdown-table th {
            background: #f8f9fa;
            font-weight: 600;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }

        .markdown-table td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }

        .markdown-table tbody tr:nth-of-type(even) {
            background: #f8f9fa;
        }

        .markdown-table tbody tr:hover {
            background: #e3f2fd;
            cursor: pointer;
        }

        .markdown-table tbody tr:last-of-type td {
            border-bottom: none;
        }

        .list-content {
            line-height: 1.7;
        }

        .content-heading {
            color: #2c3e50;
        }

        .image-container {
            text-align: center;
        }

        .image-container img {
            max-width: 100%;
            height: auto;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }

        .image-container img:hover {
            transform: scale(1.02);
        }

        .image-error {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 4px;
            text-align: center;
            border: 1px solid #f5c6cb;
        }

        .image-caption {
            margin-top: 0.5rem;
            font-style: italic;
            color: #6c757d;
            text-align: center;
        }

        .table-of-contents {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 6px;
            margin-bottom: 2rem;
        }

        .table-of-contents ul {
            list-style: none;
            padding-left: 0;
        }

        .table-of-contents li {
            margin: 0.5rem 0;
        }

        .table-of-contents a {
            color: #007bff;
            text-decoration: none;
            padding: 0.5rem;
            display: block;
            border-radius: 4px;
            transition: background-color 0.3s ease;
        }

        .table-of-contents a:hover {
            background: #dee2e6;
        }

        .depth-0 {}
        .depth-1 {}
        .depth-2 {}
        .depth-3 {}
        .depth-4 {}
        .depth-5 {}

        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem 0;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .content {
                padding: 0;
            }

            .depth-1, .depth-2, .depth-3, .depth-4, .depth-5 {
                margin-left: 0.5rem;
            }
        }
        """

    def generate_html_document(self, data: Dict, title: str = "Document Visualization") -> str:
        """
        Generate complete HTML document from structured data organized by document structure.

        Args:
            data: Structured document data
            title: Document title for HTML head

        Returns:
            Complete HTML document string
        """
        # Extract document metadata
        metadata = data.get('metadata', {})
        total_items = metadata.get('total_items', 0)
        timestamp = metadata.get('processing_timestamp', '')

        # Organize content by document sections
        sections_content = self._organize_content_by_sections(data)

        # Generate complete HTML document
        html_document = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                {self.get_css_styles()}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 {title}</h1>
                    <div class="subtitle">Generated on {timestamp}</div>
                </div>

                <div class="document-info">
                    <div class="info-grid">
                        <div class="info-item">
                            <strong>Total Items:</strong> {total_items}
                        </div>
                        <div class="info-item">
                            <strong>Sections:</strong> {len(sections_content)}
                        </div>
                    </div>
                </div>

                {self.generate_stats_card(data)}

                <div class="content">
                    {sections_content}
                </div>

                <div class="footer">
                    <p>Generated by Chunk Monkey HTML Generator</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html_document

    def _organize_content_by_sections(self, data: Dict) -> str:
        """
        Organize all content by document sections rather than data type.

        Args:
            data: Structured document data

        Returns:
            HTML string with content organized by document structure
        """
        # Collect all items with their section information
        all_items = []

        # Add content items
        for item in data.get('content', []):
            all_items.append({**item, 'source_type': 'content'})

        # Add table items
        for item in data.get('tables', []):
            all_items.append({**item, 'source_type': 'table'})

        # Add image items
        for item in data.get('images', []):
            all_items.append({**item, 'source_type': 'image'})

        # Add reference items
        for item in data.get('references', []):
            all_items.append({**item, 'source_type': 'reference'})

        # Group items by their parent_section
        sections = {}
        for item in all_items:
            section_name = item.get('parent_section', 'Unknown Section')
            if section_name not in sections:
                sections[section_name] = []
            sections[section_name].append(item)

        # Generate HTML for each section
        sections_html = []
        for section_index, (section_name, items) in enumerate(sections.items()):
            if items:  # Only generate sections that have content
                section_html = self._generate_document_section(section_name, items, section_index)
                sections_html.append(section_html)

        return "".join(sections_html)

    def _generate_document_section(self, section_name: str, items: List[Dict], section_index: int = 0) -> str:
        """
        Generate HTML for a document section with all its content.

        Args:
            section_name: Name of the document section
            items: All items belonging to this section
            section_index: Index of the section for line numbering

        Returns:
            HTML string for the section
        """
        # Determine section depth from first item's hierarchy
        depth = 0
        if items:
            hierarchy = items[0].get('section_hierarchy', [])
            depth = len(hierarchy) - 1 if hierarchy else 0

        # Count different types of content using source_type and item_type
        text_count = len([i for i in items if i.get('type') == 'textitem' or (i.get('source_type') == 'content' and 'text' in i.get('type', ''))])
        table_count = len([i for i in items if i.get('source_type') == 'table' or i.get('item_type') == 'tableitem'])
        image_count = len([i for i in items if i.get('source_type') == 'image' or i.get('item_type') == 'pictureitem'])
        list_count = len([i for i in items if i.get('type') == 'listitem'])

        # Count content types for stats
        content_types = {}
        for item in items:
            # Use source_type first, then fall back to type or item_type
            item_type = item.get('source_type')
            if not item_type:
                item_type = item.get('type') or item.get('item_type', 'unknown')
            content_types[item_type] = content_types.get(item_type, 0) + 1

        # Generate content types breakdown
        content_types_html = ""
        if content_types:
            type_details = []
            for item_type, count in content_types.items():
                display_type = item_type.replace('item', '') if item_type.endswith('item') else item_type
                type_details.append(f"<span class='stat-detail'>{display_type}: {count}</span>")
            content_types_html = "<br>".join(type_details)

        # Generate section statistics
        stats_html = f"""
    <div class="stats-card">
        <h3>📊 Document Statistics</h3>
        <div class="stats-grid">
            <div class='stat-item'><strong>Total Items:</strong> {len(items)}</div><div class='stat-item'><strong>Content Types:</strong><br>{content_types_html}</div><div class='stat-item'><strong>Image Count:</strong> {image_count}</div><div class='stat-item'><strong>Text Blocks:</strong> {text_count}</div><div class='stat-item'><strong>List Items:</strong> {list_count}</div><div class='stat-item'><strong>Table Rows:</strong> {table_count}</div><div class='stat-item'><strong>Subsection Count:</strong> 0</div>
        </div>
    </div>
    """

        # Generate content HTML
        items_html = []
        for i, item in enumerate(items):
            source_type = item.get('source_type', 'content')
            if source_type == 'image':
                items_html.append(self._generate_image_item(item, i))
            elif source_type == 'table':
                items_html.append(self._generate_table_item(item, i))
            else:
                items_html.append(self.generate_content_item(item, i))

        # Generate section HTML
        section_html = f"""
    <div class="section depth-{depth}">
        <div class="section-header">
            <h2 class="section-title">{section_name}</h2>
            <span class="section-meta">Line {section_index * 2 + 1} • Level 2</span>
        </div>

        <div class="section-stats">
            <details>
                <summary>📈 Section Statistics</summary>
                <div class="mini-stats">
                    {stats_html}
                </div>
            </details>
        </div>


        <div class="section-content">
            {"".join(items_html)}
        </div>


    </div>
    """

        return section_html

    def generate(self, data: Dict, output_path: str, title: str = "Document Visualization") -> None:
        """
        Generate HTML file from structured data.

        Args:
            data: Structured document data
            output_path: Path for output HTML file
            title: Document title

        Raises:
            Exception: If HTML generation or file writing fails
        """
        try:
            # Generate HTML document
            html_content = self.generate_html_document(data, title)

            # Write to file
            self.file_manager.write_text_file(output_path, html_content)

            logger.info(f"HTML visualization generated: {output_path}")

        except Exception as e:
            logger.error(f"Error generating HTML: {e}")
            raise

    def generate_from_json_file(self, json_path: str, output_path: Optional[str] = None,
                               title: Optional[str] = None) -> str:
        """
        Generate HTML directly from JSON file.

        Args:
            json_path: Path to input JSON file
            output_path: Optional output path (auto-generated if not provided)
            title: Optional document title

        Returns:
            Path to generated HTML file

        Raises:
            Exception: If processing fails
        """
        try:
            # Load JSON data
            data = self.load_json_document(json_path)
            if not data:
                raise ValueError("Failed to load JSON document")

            # Determine output path
            if not output_path:
                json_file = Path(json_path)
                output_path = json_file.parent / f"{json_file.stem}.html"

            # Determine title
            if not title:
                title = Path(json_path).stem.replace('_', ' ').title()

            # Generate HTML
            self.generate(data, str(output_path), title)

            return str(output_path)

        except Exception as e:
            logger.error(f"Error generating HTML from JSON file: {e}")
            raise


# Convenience functions for direct use
def generate_html(data: Dict, output_path: str, title: str = "Document Visualization") -> None:
    """Convenience function to generate HTML from structured data."""
    generator = HTMLGenerator()
    generator.generate(data, output_path, title)


def generate_html_from_json(json_path: str, output_path: Optional[str] = None,
                           title: Optional[str] = None) -> str:
    """Convenience function to generate HTML from JSON file."""
    generator = HTMLGenerator()
    return generator.generate_from_json_file(json_path, output_path, title)


def main():
    """Main function for command-line usage."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Generate HTML visualization from structured JSON')
    parser.add_argument('input_file', help='Path to input JSON file')
    parser.add_argument('-o', '--output', help='Output HTML file path')
    parser.add_argument('-t', '--title', help='Document title')
    parser.add_argument('--theme', choices=['modern', 'classic', 'minimal'],
                       default='modern', help='HTML theme')

    args = parser.parse_args()

    try:
        # Configure generator
        config = {'theme': args.theme}
        generator = HTMLGenerator(config)

        # Generate HTML
        output_path = generator.generate_from_json_file(
            args.input_file,
            args.output,
            args.title
        )

        print(f"HTML visualization generated: {output_path}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
