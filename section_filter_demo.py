#!/usr/bin/env python3
"""
Script to demonstrate filtering the structured JSON by section.
This allows users to retrieve all content from specific sections.
"""

import json
from typing import Dict, List

def load_structured_data(filename: str) -> Dict:
    """Load the structured data from JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_by_section(data: Dict, section_name: str) -> Dict[str, List]:
    """Filter the structured data to return only items from a specific section."""
    filtered_data = {
        "content": [],
        "tables": [],
        "images": [],
        "references": []
    }
    
    for category in ["content", "tables", "images", "references"]:
        for item in data.get(category, []):
            # Check if the section name matches any level in the hierarchy
            if item.get("section_hierarchy"):
                for section in item["section_hierarchy"]:
                    if section_name.lower() in section.lower():
                        filtered_data[category].append(item)
                        break
            # Also check parent_section for direct matches
            elif item.get("parent_section") and section_name.lower() in item["parent_section"].lower():
                filtered_data[category].append(item)
    
    return filtered_data

def get_available_sections(data: Dict) -> List[str]:
    """Get a list of all available main sections."""
    sections = set()
    for category in ["content", "tables", "images", "references"]:
        for item in data.get(category, []):
            if item.get("parent_section"):
                sections.add(item["parent_section"])
    return sorted(list(sections))

def get_available_subsections(data: Dict, main_section: str) -> List[str]:
    """Get a list of all subsections within a main section."""
    subsections = set()
    for category in ["content", "tables", "images", "references"]:
        for item in data.get(category, []):
            if (item.get("parent_section") == main_section and 
                item.get("subsection")):
                subsections.add(item["subsection"])
    return sorted(list(subsections))

def main():
    # Load the structured data
    data = load_structured_data("burns_structured_local.json")
    section_summary = load_structured_data("burns_section_summary.json")
    
    print("=== DOCUMENT STRUCTURE ===")
    print("Available main sections:")
    for i, section in enumerate(get_available_sections(data), 1):
        counts = section_summary.get(section, {})
        print(f"{i:2d}. {section}")
        print(f"    Content: {counts.get('content_count', 0)}, Tables: {counts.get('table_count', 0)}, "
              f"Images: {counts.get('image_count', 0)}, References: {counts.get('reference_count', 0)}")
        subsections = counts.get('subsections', [])
        if subsections:
            print(f"    Subsections: {', '.join(subsections)}")
        print()
    
    print("="*80)
    
    # Example 1: Filter content from the "ABSTRACT" section
    print("\n=== EXAMPLE 1: ABSTRACT SECTION ===")
    abstract_data = filter_by_section(data, "ABSTRACT")
    print(f"Content from 'ABSTRACT' section:")
    print(f"- {len(abstract_data['content'])} text items")
    print(f"- {len(abstract_data['tables'])} tables")
    print(f"- {len(abstract_data['images'])} images")
    
    if abstract_data['content']:
        print("\nAbstract content:")
        for item in abstract_data['content']:
            if item['type'] == 'textitem':
                print(f"• {item['text'][:200]}...")
    
    print("\n" + "="*80)
    
    # Example 2: Filter content from the "Airway" subsection
    print("\n=== EXAMPLE 2: AIRWAY SUBSECTION ===")
    airway_data = filter_by_section(data, "Airway")
    print(f"Content from 'Airway' subsection:")
    print(f"- {len(airway_data['content'])} text items")
    print(f"- {len(airway_data['tables'])} tables")
    print(f"- {len(airway_data['images'])} images")
    
    if airway_data['content']:
        print("\nFirst few items from Airway subsection:")
        for i, item in enumerate(airway_data['content'][:3], 1):
            print(f"{i}. [{item['type']}] {item['text'][:150]}...")
    
    print("\n" + "="*80)
    
    # Example 3: Filter content from the "WOUNDCARE" section
    print("\n=== EXAMPLE 3: WOUNDCARE SECTION ===")
    woundcare_data = filter_by_section(data, "WOUNDCARE")
    print(f"Content from 'WOUNDCARE' section:")
    print(f"- {len(woundcare_data['content'])} text items")
    print(f"- {len(woundcare_data['tables'])} tables")
    print(f"- {len(woundcare_data['images'])} images")
    
    if woundcare_data['content']:
        print("\nWoundcare content:")
        for item in woundcare_data['content']:
            if item['type'] == 'textitem':
                print(f"• {item['text'][:200]}...")

if __name__ == "__main__":
    main()
