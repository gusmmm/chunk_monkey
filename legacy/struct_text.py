#!/usr/bin/env python3
"""
Script to parse burns-with-image-refs.md and create a structured JSON
with nested sections based on header hierarchy.
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def determine_content_type(line: str) -> str:
    """Determine the type of content based on the line."""
    line_stripped = line.strip()
    
    if not line_stripped:
        return "empty"
    elif line_stripped.startswith('#'):
        # Count the number of # to determine header level
        level = len(line_stripped) - len(line_stripped.lstrip('#'))
        return f"header_h{level}"
    elif line_stripped.startswith('!['):
        return "image"
    elif line_stripped.startswith('|') or '|' in line_stripped:
        return "table_row"
    elif line_stripped.startswith('-') or line_stripped.startswith('*') or line_stripped.startswith('+'):
        return "list_item"
    elif line_stripped.startswith('>'):
        return "blockquote"
    elif line_stripped.startswith('```'):
        return "code_block"
    elif re.match(r'^\d+\.', line_stripped):
        return "numbered_list"
    else:
        return "text"

def extract_header_text(line: str) -> str:
    """Extract the text content from a header line."""
    return line.strip().lstrip('#').strip()

def get_header_level(line: str) -> int:
    """Get the header level (number of #)."""
    return len(line.strip()) - len(line.strip().lstrip('#'))

def parse_markdown_to_structure(file_path: str) -> Dict[str, Any]:
    """Parse markdown file and create a structured representation."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Initialize the root structure
    document = {
        "document_info": {
            "source_file": str(file_path),
            "total_lines": len(lines),
            "structure_type": "nested_sections"
        },
        "content": []
    }
    
    # Stack to keep track of current section hierarchy
    section_stack = []
    current_section = None
    
    line_number = 0
    
    for line in lines:
        line_number += 1
        content_type = determine_content_type(line)
        
        # Handle headers - they create new sections
        if content_type.startswith("header_"):
            header_level = get_header_level(line)
            header_text = extract_header_text(line)
            
            # Create new section
            new_section = {
                "type": "section",
                "level": header_level,
                "title": header_text,
                "line_number": line_number,
                "content": [],
                "subsections": []
            }
            
            # Determine where to place this section based on hierarchy
            # Pop sections from stack until we find the right parent level
            while section_stack and section_stack[-1]["level"] >= header_level:
                section_stack.pop()
            
            # Add to parent or root
            if section_stack:
                section_stack[-1]["subsections"].append(new_section)
            else:
                document["content"].append(new_section)
            
            # Update current section and stack
            section_stack.append(new_section)
            current_section = new_section
            
        else:
            # Handle non-header content
            if content_type != "empty":  # Skip empty lines
                content_item = {
                    "type": content_type,
                    "line_number": line_number,
                    "content": line.rstrip('\n')
                }
                
                # Add special processing for images
                if content_type == "image":
                    # Extract image path and alt text
                    match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
                    if match:
                        content_item["alt_text"] = match.group(1)
                        content_item["image_path"] = match.group(2)
                
                # Add to current section or root if no section exists
                if current_section:
                    current_section["content"].append(content_item)
                else:
                    # Create a default section for content before any headers
                    if not document["content"] or document["content"][-1]["type"] != "section":
                        default_section = {
                            "type": "section",
                            "level": 0,
                            "title": "Document Preamble",
                            "line_number": 1,
                            "content": [],
                            "subsections": []
                        }
                        document["content"].append(default_section)
                        current_section = default_section
                    
                    current_section["content"].append(content_item)
    
    return document

def add_content_statistics(structure: Dict[str, Any]) -> Dict[str, Any]:
    """Add content statistics to each section."""
    
    def process_section(section: Dict[str, Any]) -> Dict[str, Any]:
        if section["type"] != "section":
            return section
        
        # Count content types in this section
        content_stats = {
            "total_items": len(section["content"]),
            "content_types": {},
            "image_count": 0,
            "text_blocks": 0,
            "list_items": 0,
            "table_rows": 0
        }
        
        for item in section["content"]:
            content_type = item["type"]
            content_stats["content_types"][content_type] = content_stats["content_types"].get(content_type, 0) + 1
            
            # Update specific counters
            if content_type == "image":
                content_stats["image_count"] += 1
            elif content_type == "text":
                content_stats["text_blocks"] += 1
            elif content_type in ["list_item", "numbered_list"]:
                content_stats["list_items"] += 1
            elif content_type == "table_row":
                content_stats["table_rows"] += 1
        
        section["statistics"] = content_stats
        
        # Process subsections recursively
        for i, subsection in enumerate(section["subsections"]):
            section["subsections"][i] = process_section(subsection)
        
        # Add subsection count
        section["statistics"]["subsection_count"] = len(section["subsections"])
        
        return section
    
    # Process all top-level sections
    for i, section in enumerate(structure["content"]):
        structure["content"][i] = process_section(section)
    
    # Add document-level statistics
    total_sections = count_total_sections(structure)
    total_images = count_total_content_type(structure, "image")
    total_text_blocks = count_total_content_type(structure, "text")
    
    structure["document_info"]["statistics"] = {
        "total_sections": total_sections,
        "total_images": total_images,
        "total_text_blocks": total_text_blocks,
        "max_depth": calculate_max_depth(structure)
    }
    
    return structure

def count_total_sections(structure: Dict[str, Any]) -> int:
    """Count total number of sections in the document."""
    count = 0
    
    def count_sections(section: Dict[str, Any]) -> int:
        if section["type"] == "section":
            return 1 + sum(count_sections(sub) for sub in section["subsections"])
        return 0
    
    for section in structure["content"]:
        count += count_sections(section)
    
    return count

def count_total_content_type(structure: Dict[str, Any], content_type: str) -> int:
    """Count total items of a specific content type."""
    count = 0
    
    def count_in_section(section: Dict[str, Any]) -> int:
        section_count = 0
        for item in section.get("content", []):
            if item["type"] == content_type:
                section_count += 1
        
        for subsection in section.get("subsections", []):
            section_count += count_in_section(subsection)
        
        return section_count
    
    for section in structure["content"]:
        count += count_in_section(section)
    
    return count

def calculate_max_depth(structure: Dict[str, Any]) -> int:
    """Calculate the maximum nesting depth of sections."""
    max_depth = 0
    
    def get_depth(section: Dict[str, Any], current_depth: int = 1) -> int:
        if section["type"] != "section":
            return current_depth
        
        max_sub_depth = current_depth
        for subsection in section.get("subsections", []):
            sub_depth = get_depth(subsection, current_depth + 1)
            max_sub_depth = max(max_sub_depth, sub_depth)
        
        return max_sub_depth
    
    for section in structure["content"]:
        depth = get_depth(section)
        max_depth = max(max_depth, depth)
    
    return max_depth

def save_structured_json(structure: Dict[str, Any], output_path: str) -> None:
    """Save the structured data to a JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Structured JSON saved to: {output_file}")

def main():
    """Main function to parse markdown and create structured JSON."""
    input_file = "output/burns-with-image-refs.md"
    output_file = "output/burns_structured_markdown.json"
    
    try:
        logger.info(f"Parsing markdown file: {input_file}")
        
        # Parse the markdown file
        structure = parse_markdown_to_structure(input_file)
        
        # Add content statistics
        structure = add_content_statistics(structure)
        
        # Save to JSON
        save_structured_json(structure, output_file)
        
        # Print summary
        stats = structure["document_info"]["statistics"]
        logger.info("Processing complete!")
        logger.info(f"Total sections: {stats['total_sections']}")
        logger.info(f"Total images: {stats['total_images']}")
        logger.info(f"Total text blocks: {stats['total_text_blocks']}")
        logger.info(f"Maximum nesting depth: {stats['max_depth']}")
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise

if __name__ == "__main__":
    main()
