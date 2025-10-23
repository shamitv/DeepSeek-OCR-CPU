"""
Element extraction engine.

Parses grounding references from DeepSeek OCR output and extracts
individual elements with metadata and bounding boxes.
"""

import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from PIL import Image

from .bbox_processor import (
    denormalize_bbox_999,
    validate_bbox,
    calculate_bbox_metrics,
    clip_bbox_to_image,
)


def parse_grounding_references(text: str) -> List[Tuple[str, str]]:
    """
    Extract grounding references from model output.
    
    Format: <|ref|>{label_type}<|/ref|><|det|>{coordinates}<|/det|>
    
    Args:
        text: Raw model output text containing grounding references
    
    Returns:
        List of tuples (label_type, coordinates_str)
    """
    pattern = r'<\|ref\|>(.*?)<\|/ref\|><\|det\|>(.*?)<\|/det\|>'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def parse_coordinates(coords_str: str) -> Optional[List[List[float]]]:
    """
    Parse coordinate string to list of bounding boxes.
    
    Args:
        coords_str: String representation of coordinates (Python list format)
    
    Returns:
        List of bounding boxes, each as [x1, y1, x2, y2], or None if invalid
    """
    try:
        coords = eval(coords_str)
        if isinstance(coords, list):
            return coords
        return None
    except Exception as e:
        print(f"Warning: Failed to parse coordinates: {e}")
        return None


def extract_all_elements(
    image: Image.Image,
    model_output: str,
    page_number: int = 1,
    extract_options: Optional[Dict] = None
) -> List[Dict]:
    """
    Extract all elements from model output with metadata.
    
    Args:
        image: Source image (PIL Image)
        model_output: Raw model output text with grounding references
        page_number: Page number in document (1-indexed)
        extract_options: Optional extraction configuration
            - padding: int, pixels to add around bbox (default: 0)
            - min_width: int, minimum element width (default: 10)
            - min_height: int, minimum element height (default: 10)
            - validate_strict: bool, reject invalid bboxes (default: False)
    
    Returns:
        List of element dictionaries with structure:
        {
            'id': 'page_{page}_elem_{index}',
            'type': label_type,
            'page': page_number,
            'index': element_index,
            'bounding_boxes': [{'x1', 'y1', 'x2', 'y2'}, ...],
            'bounding_boxes_normalized': [...],  # 0-1 normalized
            'metrics': {
                'num_boxes': int,
                'total_area': float,
                'width': float,
                'height': float,
                'aspect_ratio': float,
            },
            'image_dimensions': {'width': int, 'height': int},
        }
    """
    options = extract_options or {}
    padding = options.get('padding', 0)
    min_width = options.get('min_width', 10)
    min_height = options.get('min_height', 10)
    validate_strict = options.get('validate_strict', False)
    
    image_width, image_height = image.size
    
    # Parse grounding references
    grounding_refs = parse_grounding_references(model_output)
    
    elements = []
    element_index = 0
    
    for label_type, coords_str in grounding_refs:
        # Parse coordinates
        coords_list = parse_coordinates(coords_str)
        if coords_list is None:
            continue
        
        # Convert to absolute pixels and validate
        bounding_boxes = []
        for coords in coords_list:
            if len(coords) != 4:
                continue
            
            # Create bbox dict from model coordinates (0-999 range)
            bbox_model = {
                'x1': coords[0],
                'y1': coords[1],
                'x2': coords[2],
                'y2': coords[3],
            }
            
            # Convert to absolute pixels
            bbox_abs = denormalize_bbox_999(bbox_model, image_width, image_height)
            
            # Validate
            if not validate_bbox(bbox_abs, image_width, image_height, allow_out_of_bounds=True):
                if validate_strict:
                    continue
            
            # Clip to image bounds
            bbox_abs = clip_bbox_to_image(bbox_abs, image_width, image_height)
            
            # Check minimum size
            width = bbox_abs['x2'] - bbox_abs['x1']
            height = bbox_abs['y2'] - bbox_abs['y1']
            if width < min_width or height < min_height:
                continue
            
            bounding_boxes.append(bbox_abs)
        
        # Skip if no valid boxes
        if not bounding_boxes:
            continue
        
        # Calculate metrics
        total_area = sum((b['x2'] - b['x1']) * (b['y2'] - b['y1']) for b in bounding_boxes)
        
        # Calculate overall bounding box (union of all boxes)
        min_x1 = min(b['x1'] for b in bounding_boxes)
        min_y1 = min(b['y1'] for b in bounding_boxes)
        max_x2 = max(b['x2'] for b in bounding_boxes)
        max_y2 = max(b['y2'] for b in bounding_boxes)
        
        overall_width = max_x2 - min_x1
        overall_height = max_y2 - min_y1
        overall_aspect_ratio = overall_width / overall_height if overall_height > 0 else 0.0
        
        # Normalize bounding boxes to 0-1 range
        bounding_boxes_normalized = [
            {
                'x1': b['x1'] / image_width,
                'y1': b['y1'] / image_height,
                'x2': b['x2'] / image_width,
                'y2': b['y2'] / image_height,
            }
            for b in bounding_boxes
        ]
        
        # Create element dict
        element = {
            'id': f'page_{page_number:04d}_elem_{element_index:04d}',
            'type': label_type,
            'page': page_number,
            'index': element_index,
            'bounding_boxes': bounding_boxes,
            'bounding_boxes_normalized': bounding_boxes_normalized,
            'metrics': {
                'num_boxes': len(bounding_boxes),
                'total_area': total_area,
                'width': overall_width,
                'height': overall_height,
                'aspect_ratio': overall_aspect_ratio,
            },
            'image_dimensions': {
                'width': image_width,
                'height': image_height,
            },
        }
        
        elements.append(element)
        element_index += 1
    
    return elements


def extract_element_content(
    image: Image.Image,
    element: Dict,
    padding: int = 0
) -> Optional[Image.Image]:
    """
    Extract the visual content of an element from the image.
    
    For elements with multiple bounding boxes, extracts the union bbox.
    
    Args:
        image: Source image
        element: Element dictionary with bounding_boxes
        padding: Pixels to add around element (default: 0)
    
    Returns:
        Cropped image region, or None if extraction fails
    """
    try:
        bboxes = element['bounding_boxes']
        if not bboxes:
            return None
        
        # Calculate union bounding box
        min_x1 = min(b['x1'] for b in bboxes)
        min_y1 = min(b['y1'] for b in bboxes)
        max_x2 = max(b['x2'] for b in bboxes)
        max_y2 = max(b['y2'] for b in bboxes)
        
        # Add padding
        if padding > 0:
            image_width, image_height = image.size
            min_x1 = max(0, min_x1 - padding)
            min_y1 = max(0, min_y1 - padding)
            max_x2 = min(image_width, max_x2 + padding)
            max_y2 = min(image_height, max_y2 + padding)
        
        # Crop image
        cropped = image.crop((min_x1, min_y1, max_x2, max_y2))
        return cropped
    except Exception as e:
        print(f"Warning: Failed to extract element {element.get('id', 'unknown')}: {e}")
        return None
