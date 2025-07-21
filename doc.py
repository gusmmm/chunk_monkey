import json
import base64
import re
import logging
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Any, Optional

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
from docling_core.types.doc import PictureItem, TableItem, TextItem, ListItem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def safe_get_text(item: Any) -> Optional[str]:
    """Safely extract text from an item, handling various attribute names."""
    text_attrs = ['text', 'content', 'value']
    for attr in text_attrs:
        if hasattr(item, attr):
            value = getattr(item, attr)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None

def safe_get_caption(item: Any) -> Optional[str]:
    """Safely extract caption from an item."""
    try:
        if hasattr(item, 'captions') and item.captions:
            for caption in item.captions:
                caption_text = safe_get_text(caption)
                if caption_text:
                    return caption_text
        elif hasattr(item, 'caption'):
            return safe_get_text(item.caption)
    except (AttributeError, IndexError, TypeError) as e:
        logger.debug(f"Error extracting caption: {e}")
    return None

def get_item_type(item: Any) -> str:
    """Get the type of an item as a string."""
    return type(item).__name__.lower()

def is_references_section(item: Any) -> bool:
    """Check if an item indicates the start of a references/bibliography section."""
    item_type = get_item_type(item)
    text = safe_get_text(item)
    
    if text and ('header' in item_type or 'heading' in item_type or 'section' in item_type):
        return bool(re.search(r'\b(references|bibliography|citations|works\s+cited)\b', text, re.IGNORECASE))
    return False

def configure_pipeline() -> DocumentConverter:
    """Configure and return a DocumentConverter with optimal settings."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = 2.0  # Set image resolution
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    pipeline_options.generate_table_images = True

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

def process_pdf(file_path: str) -> Any:
    """Process a PDF file and return the document object."""
    logger.info(f"Processing {file_path} with local Docling...")
    
    doc_converter = configure_pipeline()
    
    try:
        conv_res = doc_converter.convert(Path(file_path))
        logger.info("Successfully processed document.")
        return conv_res.document
    except Exception as e:
        logger.error(f"Error processing document with Docling: {e}")
        raise

def initialize_structure() -> Dict[str, List]:
    """Initialize the structured data dictionary."""
    return {
        "metadata": {
            "total_items": 0,
            "processing_timestamp": None
        },
        "content": [],
        "tables": [],
        "images": [],
        "references": []
    }

def process_table_item(item: TableItem, doc: Any) -> Dict[str, Any]:
    """Process a TableItem and return its structured representation."""
    table_content = safe_get_text(item)
    if not table_content:
        # Fallback: try to get content from other attributes
        if hasattr(item, 'data'):
            table_content = str(item.data)
        else:
            table_content = str(item)
    
    return {
        "content": table_content,
        "caption": safe_get_caption(item),
        "item_type": get_item_type(item)
    }

def process_picture_item(item: PictureItem, doc: Any) -> Optional[Dict[str, Any]]:
    """Process a PictureItem and return its structured representation."""
    try:
        # Convert PIL image to base64
        buffered = BytesIO()
        pil_image = item.get_image(doc)
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {
            "base64_data": img_str,
            "caption": safe_get_caption(item),
            "item_type": get_item_type(item)
        }
    except Exception as e:
        logger.warning(f"Error processing image: {e}")
        return None

def process_text_item(item: Any) -> Optional[Dict[str, Any]]:
    """Process a text-based item and return its structured representation."""
    text = safe_get_text(item)
    if text:
        return {
            "type": get_item_type(item),
            "text": text
        }
    return None

def is_main_header(item: Any) -> bool:
    """Determine if an item is a main section header based on formatting and content."""
    item_type = get_item_type(item)
    text = safe_get_text(item)
    
    if not text or not ('header' in item_type or 'heading' in item_type or 'section' in item_type):
        return False
    
    # Check for main header indicators
    text_upper = text.upper()
    
    # Main headers are typically:
    # 1. All caps or mostly caps
    # 2. Longer descriptive titles
    # 3. Common section keywords
    main_keywords = ['abstract', 'introduction', 'methods', 'methodology', 'results', 'discussion', 
                     'conclusion', 'references', 'bibliography', 'acknowledgments', 'appendix']
    
    # Check if it's a main header
    if (len(text) > 40 or  # Long descriptive titles
        text.isupper() or  # All uppercase
        any(keyword in text.lower() for keyword in main_keywords) or  # Contains main keywords
        text.endswith(':')):  # Ends with colon (like "ABSTRACT:")
        return True
    
    return False

def extract_structured_data(doc: Any) -> Dict[str, Any]:
    """Extract and structure content from the document."""
    structured_data = initialize_structure()
    in_references_section = False
    item_count = 0
    current_main_section = None
    current_subsection = None
    section_hierarchy = []
    
    logger.info("Extracting and structuring content...")
    
    for item, _ in doc.iterate_items():
        item_count += 1
        item_type = get_item_type(item)
        
        # Check if this is a header/section item
        if 'header' in item_type or 'heading' in item_type or 'section' in item_type:
            text = safe_get_text(item)
            if text:
                if is_main_header(item):
                    # This is a main section header
                    current_main_section = text
                    current_subsection = None
                    section_hierarchy = [current_main_section]
                    
                    # Check if this is the references section
                    if is_references_section(item):
                        in_references_section = True
                        logger.info("Detected references section")
                else:
                    # This is a subsection header
                    current_subsection = text
                    if current_main_section:
                        section_hierarchy = [current_main_section, current_subsection]
                    else:
                        section_hierarchy = [current_subsection]
        
        # Process items based on type and add section context
        if in_references_section:
            text_data = process_text_item(item)
            if text_data:
                text_data["section_hierarchy"] = section_hierarchy.copy()
                text_data["parent_section"] = current_main_section
                text_data["subsection"] = current_subsection
                structured_data["references"].append(text_data)
        elif isinstance(item, TableItem):
            table_data = process_table_item(item, doc)
            table_data["label"] = f"table_{len(structured_data['tables']) + 1}"
            table_data["section_hierarchy"] = section_hierarchy.copy()
            table_data["parent_section"] = current_main_section
            table_data["subsection"] = current_subsection
            structured_data["tables"].append(table_data)
        elif isinstance(item, PictureItem):
            image_data = process_picture_item(item, doc)
            if image_data:
                image_data["label"] = f"image_{len(structured_data['images']) + 1}"
                image_data["section_hierarchy"] = section_hierarchy.copy()
                image_data["parent_section"] = current_main_section
                image_data["subsection"] = current_subsection
                structured_data["images"].append(image_data)
        else:
            text_data = process_text_item(item)
            if text_data:
                text_data["section_hierarchy"] = section_hierarchy.copy()
                text_data["parent_section"] = current_main_section
                text_data["subsection"] = current_subsection
                structured_data["content"].append(text_data)
    
    # Update metadata
    from datetime import datetime
    structured_data["metadata"]["total_items"] = item_count
    structured_data["metadata"]["processing_timestamp"] = datetime.now().isoformat()
    
    logger.info(f"Processed {item_count} items total")
    logger.info(f"Found {len(structured_data['content'])} content items")
    logger.info(f"Found {len(structured_data['tables'])} tables")
    logger.info(f"Found {len(structured_data['images'])} images")
    logger.info(f"Found {len(structured_data['references'])} reference items")
    
    return structured_data

def save_to_json(data: Dict, filename: str) -> None:
    """Save structured data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully saved structured data to {filename}")
    except Exception as e:
        logger.error(f"Error saving JSON file: {e}")
        raise

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

def get_section_summary(data: Dict) -> Dict[str, Dict]:
    """Get a summary of all sections and their content counts."""
    sections = {}
    
    for category in ["content", "tables", "images", "references"]:
        for item in data.get(category, []):
            parent = item.get("parent_section", "Unknown")
            subsection = item.get("subsection")
            
            if parent not in sections:
                sections[parent] = {
                    "content_count": 0,
                    "table_count": 0,
                    "image_count": 0,
                    "reference_count": 0,
                    "subsections": set()
                }
            
            # Map category names to count keys
            count_key_map = {
                "content": "content_count",
                "tables": "table_count", 
                "images": "image_count",
                "references": "reference_count"
            }
            
            sections[parent][count_key_map[category]] += 1
            if subsection:
                sections[parent]["subsections"].add(subsection)
    
    # Convert sets to lists for JSON serialization
    for section in sections.values():
        section["subsections"] = sorted(list(section["subsections"]))
    
    return sections

def main():
    """Main function to process the PDF and generate structured JSON."""
    try:
        # Process the PDF
        doc = process_pdf("burns.pdf")
        
        # Extract structured data
        structured_data = extract_structured_data(doc)
        
        # Save to JSON file
        output_filename = 'burns_structured_local.json'
        save_to_json(structured_data, output_filename)
        
        # Generate and save section summary
        section_summary = get_section_summary(structured_data)
        save_to_json(section_summary, 'burns_section_summary.json')
        
        # Print section summary
        logger.info("Section Summary:")
        for section_name, counts in section_summary.items():
            logger.info(f"  {section_name}:")
            logger.info(f"    Content: {counts['content_count']}, Tables: {counts['table_count']}, "
                       f"Images: {counts['image_count']}, References: {counts['reference_count']}")
            if counts['subsections']:
                logger.info(f"    Subsections: {', '.join(counts['subsections'])}")
        
        # Example: Save filtered data for a specific section
        # airway_section = filter_by_section(structured_data, "Airway")
        # save_to_json(airway_section, 'burns_airway_section.json')
        
    except Exception as e:
        logger.error(f"Error in main processing: {e}")
        raise

if __name__ == "__main__":
    main()

