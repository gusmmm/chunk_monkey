#!/usr/bin/env python3
"""
Document Structure Visualizer

A generic script to create beautiful HTML visualizations of structured JSON documents.
Supports nested sections, content types, images, and statistics.
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime


def load_json_document(file_path):
    """Load and parse the JSON document."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None


def generate_stats_card(stats):
    """Generate HTML for document statistics."""
    if not stats:
        return ""
    
    stat_items = []
    for key, value in stats.items():
        formatted_key = key.replace('_', ' ').title()
        if isinstance(value, dict):
            # Handle nested stats like content_types
            nested_items = []
            for sub_key, sub_value in value.items():
                nested_items.append(f"<span class='stat-detail'>{sub_key}: {sub_value}</span>")
            stat_items.append(f"<div class='stat-item'><strong>{formatted_key}:</strong><br>{'<br>'.join(nested_items)}</div>")
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


def generate_content_item(item, base_path=""):
    """Generate HTML for a single content item."""
    content_type = item.get('type', 'text')
    content_text = item.get('content', '')
    line_number = item.get('line_number', '')
    image_path = item.get('image_path', '')
    
    # Handle different content types
    if content_type == 'image' or image_path:
        # Try to find the image relative to the JSON file
        img_src = image_path if image_path else content_text
        if base_path and not os.path.isabs(img_src):
            img_src = os.path.join(base_path, img_src)
        
        return f"""
        <div class="content-item image-item">
            <div class="content-meta">📷 Image (Line {line_number})</div>
            <div class="image-container">
                <img src="{img_src}" alt="Document Image" loading="lazy">
                <div class="image-caption">{os.path.basename(img_src)}</div>
            </div>
        </div>
        """
    
    elif content_type in ['numbered_list', 'bulleted_list', 'list']:
        return f"""
        <div class="content-item list-item">
            <div class="content-meta">📝 List Item (Line {line_number})</div>
            <div class="list-content">{content_text}</div>
        </div>
        """
    
    elif content_type == 'heading':
        level = item.get('level', 2)
        return f"""
        <div class="content-item heading-item">
            <div class="content-meta">📋 Heading Level {level} (Line {line_number})</div>
            <h{level} class="content-heading">{content_text}</h{level}>
        </div>
        """
    
    else:  # text or other types
        # Truncate very long text for better display
        display_text = content_text
        if len(display_text) > 500:
            display_text = display_text[:500] + "..."
        
        return f"""
        <div class="content-item text-item">
            <div class="content-meta">📄 Text (Line {line_number})</div>
            <div class="text-content">{display_text}</div>
        </div>
        """


def generate_section(section, base_path="", depth=0):
    """Generate HTML for a document section recursively."""
    title = section.get('title', 'Untitled Section')
    level = section.get('level', 2)
    line_number = section.get('line_number', '')
    content = section.get('content', [])
    subsections = section.get('subsections', [])
    stats = section.get('statistics', {})
    
    # Create indentation based on depth
    indent_class = f"depth-{min(depth, 5)}"
    
    # Generate content items
    content_html = ""
    if content:
        content_items = []
        for item in content:
            content_items.append(generate_content_item(item, base_path))
        content_html = f"""
        <div class="section-content">
            {''.join(content_items)}
        </div>
        """
    
    # Generate statistics if available
    stats_html = ""
    if stats and any(stats.values()):
        stats_html = f"""
        <div class="section-stats">
            <details>
                <summary>📈 Section Statistics</summary>
                <div class="mini-stats">
                    {generate_stats_card(stats)}
                </div>
            </details>
        </div>
        """
    
    # Generate subsections recursively
    subsections_html = ""
    if subsections:
        subsection_items = []
        for subsection in subsections:
            subsection_items.append(generate_section(subsection, base_path, depth + 1))
        subsections_html = f"""
        <div class="subsections">
            {''.join(subsection_items)}
        </div>
        """
    
    return f"""
    <div class="section {indent_class}">
        <div class="section-header">
            <h{level} class="section-title">{title}</h{level}>
            <span class="section-meta">Line {line_number} • Level {level}</span>
        </div>
        {stats_html}
        {content_html}
        {subsections_html}
    </div>
    """


def generate_html_document(data, output_path):
    """Generate the complete HTML document."""
    doc_info = data.get('document_info', {})
    content = data.get('content', [])
    
    # Extract document metadata
    source_file = doc_info.get('source_file', 'Unknown')
    total_lines = doc_info.get('total_lines', 0)
    structure_type = doc_info.get('structure_type', 'document')
    stats = doc_info.get('statistics', {})
    
    # Get base path for relative image paths
    base_path = os.path.dirname(output_path)
    
    # Generate main content
    sections_html = []
    for section in content:
        sections_html.append(generate_section(section, base_path))
    
    # Generate document statistics
    doc_stats_html = generate_stats_card(stats)
    
    # Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Visualization: {os.path.basename(source_file)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            opacity: 0.8;
            font-size: 1.1rem;
        }}
        
        .document-info {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .stats-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            font-size: 0.9rem;
        }}
        
        .stat-detail {{
            display: block;
            margin-left: 10px;
            font-size: 0.8rem;
            color: #666;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin: 20px 0;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}
        
        .section-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .section-title {{
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .section-meta {{
            color: #666;
            font-size: 0.9rem;
            font-weight: normal;
        }}
        
        .section-stats {{
            padding: 15px 20px;
            background: #f1f3f4;
        }}
        
        .section-stats details summary {{
            cursor: pointer;
            font-weight: 500;
            color: #555;
        }}
        
        .mini-stats .stats-card {{
            margin: 10px 0;
            padding: 15px;
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        .content-item {{
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .text-item {{
            background: #f8f9fa;
            border-left-color: #3498db;
        }}
        
        .image-item {{
            background: #e8f5e8;
            border-left-color: #27ae60;
        }}
        
        .list-item {{
            background: #fff3cd;
            border-left-color: #ffc107;
        }}
        
        .heading-item {{
            background: #e7f3ff;
            border-left-color: #007bff;
        }}
        
        .content-meta {{
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .text-content {{
            line-height: 1.7;
        }}
        
        .list-content {{
            font-weight: 500;
        }}
        
        .content-heading {{
            color: #2c3e50;
        }}
        
        .image-container {{
            text-align: center;
        }}
        
        .image-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .image-caption {{
            margin-top: 10px;
            font-size: 0.9rem;
            color: #666;
            font-style: italic;
        }}
        
        .depth-0 {{ margin-left: 0; }}
        .depth-1 {{ margin-left: 20px; }}
        .depth-2 {{ margin-left: 40px; }}
        .depth-3 {{ margin-left: 60px; }}
        .depth-4 {{ margin-left: 80px; }}
        .depth-5 {{ margin-left: 100px; }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9rem;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .depth-1, .depth-2, .depth-3, .depth-4, .depth-5 {{
                margin-left: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 Document Visualization</h1>
            <div class="subtitle">{os.path.basename(source_file)}</div>
        </div>
        
        <div class="document-info">
            <div class="info-grid">
                <div class="info-item">
                    <strong>📁 Source File:</strong><br>
                    {source_file}
                </div>
                <div class="info-item">
                    <strong>📏 Total Lines:</strong><br>
                    {total_lines:,}
                </div>
                <div class="info-item">
                    <strong>🏗️ Structure Type:</strong><br>
                    {structure_type.replace('_', ' ').title()}
                </div>
                <div class="info-item">
                    <strong>⏰ Generated:</strong><br>
                    {timestamp}
                </div>
            </div>
            
            {doc_stats_html}
        </div>
        
        <div class="content">
            {''.join(sections_html)}
        </div>
        
        <div class="footer">
            Generated by Document Structure Visualizer • {timestamp}
        </div>
    </div>
</body>
</html>
    """
    
    return html_content


def main():
    parser = argparse.ArgumentParser(description='Generate beautiful HTML visualization of structured JSON documents')
    parser.add_argument('input_file', help='Path to the input JSON file')
    parser.add_argument('-o', '--output', help='Output HTML file path (default: input_filename.html)')
    parser.add_argument('--open', action='store_true', help='Open the generated HTML file in default browser')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    # Load JSON document
    print(f"Loading document: {args.input_file}")
    data = load_json_document(args.input_file)
    if not data:
        return 1
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        input_path = Path(args.input_file)
        output_path = input_path.with_suffix('.html')
    
    # Generate HTML
    print(f"Generating visualization...")
    html_content = generate_html_document(data, str(output_path))
    
    # Write output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Visualization saved to: {output_path}")
        
        # Optionally open in browser
        if args.open:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(output_path)}")
            print(f"🌐 Opened in default browser")
            
    except Exception as e:
        print(f"Error writing output file: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
