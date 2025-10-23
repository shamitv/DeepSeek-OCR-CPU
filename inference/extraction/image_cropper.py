"""
Image cropping utilities for element extraction.

Saves individual element images with metadata.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from PIL import Image

from .element_extractor import extract_element_content


def crop_and_save_element(
    image: Image.Image,
    element: Dict,
    output_dir: Path,
    padding: int = 0,
    save_metadata: bool = True
) -> Optional[Path]:
    """
    Crop and save an individual element image with metadata.
    
    Args:
        image: Source image
        element: Element dictionary from extract_all_elements
        output_dir: Directory to save element image and metadata
        padding: Pixels to add around element (default: 0)
        save_metadata: Whether to save accompanying JSON metadata (default: True)
    
    Returns:
        Path to saved image file, or None if save failed
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract element content
        element_image = extract_element_content(image, element, padding)
        if element_image is None:
            return None
        
        # Generate filename
        element_id = element['id']
        element_type = element['type']
        image_filename = f"{element_id}_{element_type}.jpg"
        image_path = output_dir / image_filename
        
        # Save image
        element_image.save(image_path, quality=95)
        
        # Save metadata
        if save_metadata:
            metadata_filename = f"{element_id}_{element_type}.json"
            metadata_path = output_dir / metadata_filename
            
            # Create metadata dict
            metadata = {
                'element_id': element['id'],
                'type': element['type'],
                'page': element['page'],
                'index': element['index'],
                'bounding_boxes': element['bounding_boxes'],
                'bounding_boxes_normalized': element['bounding_boxes_normalized'],
                'metrics': element['metrics'],
                'image_dimensions': element['image_dimensions'],
                'cropped_image': {
                    'filename': image_filename,
                    'width': element_image.width,
                    'height': element_image.height,
                    'padding': padding,
                },
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        
        return image_path
    
    except Exception as e:
        print(f"Error saving element {element.get('id', 'unknown')}: {e}")
        return None


def save_all_elements(
    image: Image.Image,
    elements: list[Dict],
    output_dir: Path,
    padding: int = 0,
    save_metadata: bool = True
) -> Dict[str, Path]:
    """
    Save all elements as individual images with metadata.
    
    Args:
        image: Source image
        elements: List of element dictionaries
        output_dir: Directory to save elements
        padding: Pixels to add around elements (default: 0)
        save_metadata: Whether to save JSON metadata (default: True)
    
    Returns:
        Dictionary mapping element IDs to saved image paths
    """
    saved_paths = {}
    
    for element in elements:
        image_path = crop_and_save_element(
            image, element, output_dir, padding, save_metadata
        )
        if image_path:
            saved_paths[element['id']] = image_path
    
    return saved_paths
