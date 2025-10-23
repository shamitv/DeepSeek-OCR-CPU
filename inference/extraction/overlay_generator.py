"""
Overlay generator for type-specific bounding box visualizations.

Creates separate overlay images for each element type.
"""

from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np


# Color scheme for different element types
TYPE_COLORS = {
    'title': (255, 0, 0),      # Red
    'paragraph': (0, 255, 0),   # Green
    'image': (0, 0, 255),       # Blue
    'table': (255, 165, 0),     # Orange
    'equation': (255, 0, 255),  # Magenta
    'caption': (0, 255, 255),   # Cyan
    'list': (255, 255, 0),      # Yellow
    'header': (128, 0, 128),    # Purple
    'footer': (128, 128, 128),  # Gray
}

DEFAULT_COLOR = (200, 200, 200)  # Light gray for unknown types


def get_color_for_type(element_type: str) -> tuple:
    """Get RGB color for element type."""
    return TYPE_COLORS.get(element_type, DEFAULT_COLOR)


def draw_element_boxes(
    draw: ImageDraw.Draw,
    overlay: ImageDraw.Draw,
    elements: List[Dict],
    color: tuple,
    font: Optional[ImageFont.FreeTypeFont] = None,
    line_width: int = 2
) -> None:
    """
    Draw bounding boxes for a list of elements.
    
    Args:
        draw: ImageDraw object for main image
        overlay: ImageDraw object for semi-transparent overlay
        elements: List of element dictionaries
        color: RGB color tuple
        font: Font for labels (optional)
        line_width: Width of bounding box lines
    """
    if font is None:
        font = ImageFont.load_default()
    
    color_alpha = color + (20,)  # Semi-transparent fill
    
    for element in elements:
        element_type = element['type']
        
        for bbox in element['bounding_boxes']:
            x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
            
            # Draw bounding box
            if element_type == 'title':
                # Thicker lines for titles
                draw.rectangle([x1, y1, x2, y2], outline=color, width=4)
            else:
                draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)
            
            # Draw semi-transparent fill
            overlay.rectangle([x1, y1, x2, y2], fill=color_alpha, outline=(0, 0, 0, 0))
            
            # Draw label
            try:
                text_x = x1
                text_y = max(0, y1 - 15)
                
                text_bbox = draw.textbbox((0, 0), element_type, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # White background for text
                draw.rectangle(
                    [text_x, text_y, text_x + text_width, text_y + text_height],
                    fill=(255, 255, 255, 30)
                )
                
                draw.text((text_x, text_y), element_type, font=font, fill=color)
            except:
                pass


def generate_type_overlay(
    image: Image.Image,
    elements: List[Dict],
    element_type: str,
    font: Optional[ImageFont.FreeTypeFont] = None
) -> Image.Image:
    """
    Generate overlay image showing only one element type.
    
    Args:
        image: Source image
        elements: All elements
        element_type: Type to visualize
        font: Font for labels (optional)
    
    Returns:
        Image with bounding boxes for specified type
    """
    # Filter elements by type
    filtered_elements = [e for e in elements if e['type'] == element_type]
    
    if not filtered_elements:
        # Return original image if no elements of this type
        return image.copy()
    
    # Create drawing contexts
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw)
    overlay = Image.new('RGBA', img_draw.size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(overlay)
    
    # Get color for this type
    color = get_color_for_type(element_type)
    
    # Draw boxes
    draw_element_boxes(draw, draw2, filtered_elements, color, font)
    
    # Composite overlay
    img_draw.paste(overlay, (0, 0), overlay)
    
    return img_draw


def generate_all_types_overlay(
    image: Image.Image,
    elements: List[Dict],
    font: Optional[ImageFont.FreeTypeFont] = None
) -> Image.Image:
    """
    Generate overlay showing all element types with different colors.
    
    Args:
        image: Source image
        elements: All elements
        font: Font for labels (optional)
    
    Returns:
        Image with color-coded bounding boxes for all types
    """
    if not elements:
        return image.copy()
    
    # Create drawing contexts
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw)
    overlay = Image.new('RGBA', img_draw.size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(overlay)
    
    # Group elements by type
    elements_by_type = {}
    for element in elements:
        element_type = element['type']
        if element_type not in elements_by_type:
            elements_by_type[element_type] = []
        elements_by_type[element_type].append(element)
    
    # Draw each type with its color
    for element_type, type_elements in elements_by_type.items():
        color = get_color_for_type(element_type)
        draw_element_boxes(draw, draw2, type_elements, color, font)
    
    # Composite overlay
    img_draw.paste(overlay, (0, 0), overlay)
    
    return img_draw


def generate_type_overlays(
    image: Image.Image,
    elements: List[Dict],
    output_dir: Path,
    font: Optional[ImageFont.FreeTypeFont] = None
) -> Dict[str, Path]:
    """
    Generate and save type-specific overlay images.
    
    Creates separate overlay images for each element type found,
    plus one combined overlay with all types color-coded.
    
    Args:
        image: Source image
        elements: List of all elements
        output_dir: Directory to save overlay images
        font: Font for labels (optional)
    
    Returns:
        Dictionary mapping overlay type to saved file path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    saved_overlays = {}
    
    if not elements:
        return saved_overlays
    
    # Get unique element types
    element_types = sorted(set(e['type'] for e in elements))
    
    # Generate per-type overlays
    for element_type in element_types:
        overlay_image = generate_type_overlay(image, elements, element_type, font)
        
        # Save overlay
        filename = f"{element_type}_only.jpg"
        filepath = output_dir / filename
        overlay_image.save(filepath, quality=95)
        
        saved_overlays[element_type] = filepath
    
    # Generate combined overlay with all types
    all_types_overlay = generate_all_types_overlay(image, elements, font)
    all_types_path = output_dir / "all_types_colored.jpg"
    all_types_overlay.save(all_types_path, quality=95)
    saved_overlays['all_types'] = all_types_path
    
    return saved_overlays
