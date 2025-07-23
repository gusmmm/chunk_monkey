#!/usr/bin/env python3
"""
Create a simplified structure overview of the document.
"""

import json

def create_structure_overview():
    """Create a simplified overview of the document structure."""
    
    with open("output/burns_structured_markdown.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    overview = {
        "document_title": "Initial management of patients with burns and combined injuries for acute care surgeons",
        "statistics": data["document_info"]["statistics"],
        "sections": []
    }
    
    for section in data["content"]:
        if section["type"] == "section":
            section_info = {
                "title": section["title"],
                "level": section["level"],
                "content_summary": {
                    "total_items": section["statistics"]["total_items"],
                    "text_blocks": section["statistics"]["text_blocks"],
                    "images": section["statistics"]["image_count"],
                    "content_types": section["statistics"]["content_types"]
                }
            }
            overview["sections"].append(section_info)
    
    # Save overview
    with open("output/burns_structure_overview.json", 'w', encoding='utf-8') as f:
        json.dump(overview, f, indent=2, ensure_ascii=False)
    
    print("Structure overview saved to: output/burns_structure_overview.json")

if __name__ == "__main__":
    create_structure_overview()
