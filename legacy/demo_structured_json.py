#!/usr/bin/env python3
"""
Demonstration script to show how to work with the structured markdown JSON.
This shows how to filter and extract content by type and section.
"""

import json
from typing import Dict, List, Any

def load_structured_data(file_path: str) -> Dict[str, Any]:
    """Load the structured JSON data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_sections_with_images(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find all sections that contain images."""
    sections_with_images = []
    
    def search_sections(sections: List[Dict[str, Any]]):
        for section in sections:
            if section.get("statistics", {}).get("image_count", 0) > 0:
                sections_with_images.append({
                    "title": section["title"],
                    "level": section["level"],
                    "image_count": section["statistics"]["image_count"],
                    "total_content": section["statistics"]["total_items"]
                })
            
            # Search subsections recursively
            if section.get("subsections"):
                search_sections(section["subsections"])
    
    search_sections(data["content"])
    return sections_with_images

def extract_all_images(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract all image references from the document."""
    images = []
    
    def extract_from_sections(sections: List[Dict[str, Any]], parent_title: str = ""):
        for section in sections:
            section_path = f"{parent_title} > {section['title']}" if parent_title else section['title']
            
            # Extract images from this section
            for item in section.get("content", []):
                if item["type"] == "image":
                    images.append({
                        "section_path": section_path,
                        "line_number": item["line_number"],
                        "image_path": item["image_path"],
                        "alt_text": item["alt_text"]
                    })
            
            # Process subsections
            if section.get("subsections"):
                extract_from_sections(section["subsections"], section_path)
    
    extract_from_sections(data["content"])
    return images

def get_section_by_title(data: Dict[str, Any], title_search: str) -> List[Dict[str, Any]]:
    """Find sections by title (case-insensitive partial match)."""
    matching_sections = []
    
    def search_sections(sections: List[Dict[str, Any]], parent_path: str = ""):
        for section in sections:
            if title_search.lower() in section["title"].lower():
                section_path = f"{parent_path} > {section['title']}" if parent_path else section['title']
                matching_sections.append({
                    "title": section["title"],
                    "level": section["level"],
                    "path": section_path,
                    "statistics": section["statistics"],
                    "content_preview": section["content"][:2] if section["content"] else []
                })
            
            # Search subsections
            if section.get("subsections"):
                search_sections(section["subsections"], section_path if 'section_path' in locals() else section["title"])
    
    search_sections(data["content"])
    return matching_sections

def print_document_summary(data: Dict[str, Any]):
    """Print a summary of the document structure."""
    stats = data["document_info"]["statistics"]
    
    print("=== DOCUMENT SUMMARY ===")
    print(f"Source: {data['document_info']['source_file']}")
    print(f"Total lines: {data['document_info']['total_lines']}")
    print(f"Total sections: {stats['total_sections']}")
    print(f"Total images: {stats['total_images']}")
    print(f"Total text blocks: {stats['total_text_blocks']}")
    print(f"Maximum nesting depth: {stats['max_depth']}")
    print()

def print_section_structure(data: Dict[str, Any], max_depth: int = 2):
    """Print the hierarchical structure of sections."""
    print("=== SECTION STRUCTURE ===")
    
    def print_sections(sections: List[Dict[str, Any]], depth: int = 0):
        if depth >= max_depth:
            return
            
        for section in sections:
            indent = "  " * depth
            stats = section["statistics"]
            print(f"{indent}{'#' * section['level']} {section['title']}")
            print(f"{indent}   Content: {stats['total_items']} items "
                  f"(Text: {stats['text_blocks']}, Images: {stats['image_count']})")
            
            if section.get("subsections") and depth < max_depth - 1:
                print_sections(section["subsections"], depth + 1)
    
    print_sections(data["content"])
    print()

def main():
    # Load the structured data
    data = load_structured_data("output/burns_structured_markdown.json")
    
    # Print document summary
    print_document_summary(data)
    
    # Print section structure
    print_section_structure(data)
    
    # Find sections with images
    print("=== SECTIONS WITH IMAGES ===")
    image_sections = find_sections_with_images(data)
    for section in image_sections:
        print(f"• {section['title']} (Level {section['level']})")
        print(f"  Images: {section['image_count']}, Total content: {section['total_content']}")
    print()
    
    # Extract all images
    print("=== ALL IMAGES ===")
    all_images = extract_all_images(data)
    for i, img in enumerate(all_images, 1):
        print(f"{i:2d}. {img['section_path']}")
        print(f"    Path: {img['image_path']}")
        print(f"    Line: {img['line_number']}")
    print()
    
    # Search for specific sections
    print("=== AIRWAY SECTIONS ===")
    airway_sections = get_section_by_title(data, "airway")
    for section in airway_sections:
        print(f"• {section['title']} (Level {section['level']})")
        print(f"  Path: {section['path']}")
        print(f"  Content: {section['statistics']['total_items']} items")
        if section['content_preview']:
            print(f"  Preview: {section['content_preview'][0]['content'][:100]}...")
    print()
    
    # Search for circulation content
    print("=== CIRCULATION SECTIONS ===")
    circulation_sections = get_section_by_title(data, "circulation")
    for section in circulation_sections:
        print(f"• {section['title']} (Level {section['level']})")
        print(f"  Content: {section['statistics']['total_items']} items")

if __name__ == "__main__":
    main()
