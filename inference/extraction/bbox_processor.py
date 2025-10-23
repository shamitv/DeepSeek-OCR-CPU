"""
Bounding box processing utilities.

Provides functions for coordinate transformations, validation,
and geometric operations on bounding boxes.
"""

from typing import Dict, Tuple, Optional


def normalize_bbox(
    bbox: Dict[str, float],
    image_width: int,
    image_height: int
) -> Dict[str, float]:
    """
    Convert absolute coordinates to normalized [0,1] range.
    
    Args:
        bbox: Bounding box with keys 'x1', 'y1', 'x2', 'y2' in absolute pixels
        image_width: Image width in pixels
        image_height: Image height in pixels
    
    Returns:
        Normalized bounding box with values in [0,1] range
    """
    return {
        'x1': bbox['x1'] / image_width,
        'y1': bbox['y1'] / image_height,
        'x2': bbox['x2'] / image_width,
        'y2': bbox['y2'] / image_height,
    }


def denormalize_bbox(
    bbox: Dict[str, float],
    image_width: int,
    image_height: int
) -> Dict[str, int]:
    """
    Convert normalized coordinates to absolute pixels.
    
    Note: DeepSeek model uses 0-999 normalized coordinates, not 0-1.
    This function handles standard 0-1 normalization.
    
    Args:
        bbox: Bounding box with normalized coordinates in [0,1]
        image_width: Image width in pixels
        image_height: Image height in pixels
    
    Returns:
        Bounding box with absolute pixel coordinates
    """
    return {
        'x1': int(bbox['x1'] * image_width),
        'y1': int(bbox['y1'] * image_height),
        'x2': int(bbox['x2'] * image_width),
        'y2': int(bbox['y2'] * image_height),
    }


def denormalize_bbox_999(
    bbox: Dict[str, float],
    image_width: int,
    image_height: int
) -> Dict[str, int]:
    """
    Convert DeepSeek model coordinates (0-999) to absolute pixels.
    
    Args:
        bbox: Bounding box with coordinates in [0,999] range
        image_width: Image width in pixels
        image_height: Image height in pixels
    
    Returns:
        Bounding box with absolute pixel coordinates
    """
    return {
        'x1': int(bbox['x1'] / 999 * image_width),
        'y1': int(bbox['y1'] / 999 * image_height),
        'x2': int(bbox['x2'] / 999 * image_width),
        'y2': int(bbox['y2'] / 999 * image_height),
    }


def validate_bbox(
    bbox: Dict[str, float],
    image_width: int,
    image_height: int,
    allow_out_of_bounds: bool = False
) -> bool:
    """
    Check if bounding box is valid and within image bounds.
    
    Args:
        bbox: Bounding box to validate
        image_width: Image width in pixels
        image_height: Image height in pixels
        allow_out_of_bounds: If True, allow boxes partially outside image
    
    Returns:
        True if bbox is valid, False otherwise
    """
    try:
        x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
        
        # Check valid ordering
        if x1 >= x2 or y1 >= y2:
            return False
        
        # Check non-negative
        if x1 < 0 or y1 < 0:
            return False
        
        # Check bounds
        if not allow_out_of_bounds:
            if x2 > image_width or y2 > image_height:
                return False
        
        return True
    except (KeyError, TypeError):
        return False


def add_padding(
    bbox: Dict[str, int],
    padding: int,
    image_width: int,
    image_height: int
) -> Dict[str, int]:
    """
    Add padding around bounding box, clipping to image bounds.
    
    Args:
        bbox: Bounding box with absolute pixel coordinates
        padding: Padding amount in pixels
        image_width: Image width in pixels
        image_height: Image height in pixels
    
    Returns:
        Padded bounding box clipped to image boundaries
    """
    return {
        'x1': max(0, bbox['x1'] - padding),
        'y1': max(0, bbox['y1'] - padding),
        'x2': min(image_width, bbox['x2'] + padding),
        'y2': min(image_height, bbox['y2'] + padding),
    }


def calculate_bbox_metrics(bbox: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate width, height, area, and aspect ratio of bounding box.
    
    Args:
        bbox: Bounding box with keys 'x1', 'y1', 'x2', 'y2'
    
    Returns:
        Dictionary with metrics: width, height, area, aspect_ratio
    """
    width = bbox['x2'] - bbox['x1']
    height = bbox['y2'] - bbox['y1']
    area = width * height
    aspect_ratio = width / height if height > 0 else 0.0
    
    return {
        'width': width,
        'height': height,
        'area': area,
        'aspect_ratio': aspect_ratio,
    }


def check_overlap(bbox1: Dict[str, float], bbox2: Dict[str, float]) -> float:
    """
    Calculate IoU (Intersection over Union) between two bounding boxes.
    
    Args:
        bbox1: First bounding box
        bbox2: Second bounding box
    
    Returns:
        IoU value in [0,1], where 0 = no overlap, 1 = complete overlap
    """
    # Calculate intersection coordinates
    x1_inter = max(bbox1['x1'], bbox2['x1'])
    y1_inter = max(bbox1['y1'], bbox2['y1'])
    x2_inter = min(bbox1['x2'], bbox2['x2'])
    y2_inter = min(bbox1['y2'], bbox2['y2'])
    
    # Check if there is an intersection
    if x1_inter >= x2_inter or y1_inter >= y2_inter:
        return 0.0
    
    # Calculate areas
    inter_area = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    bbox1_area = (bbox1['x2'] - bbox1['x1']) * (bbox1['y2'] - bbox1['y1'])
    bbox2_area = (bbox2['x2'] - bbox2['x1']) * (bbox2['y2'] - bbox2['y1'])
    union_area = bbox1_area + bbox2_area - inter_area
    
    # Calculate IoU
    iou = inter_area / union_area if union_area > 0 else 0.0
    
    return iou


def clip_bbox_to_image(
    bbox: Dict[str, int],
    image_width: int,
    image_height: int
) -> Dict[str, int]:
    """
    Clip bounding box to image boundaries.
    
    Args:
        bbox: Bounding box with absolute pixel coordinates
        image_width: Image width in pixels
        image_height: Image height in pixels
    
    Returns:
        Clipped bounding box
    """
    return {
        'x1': max(0, min(bbox['x1'], image_width)),
        'y1': max(0, min(bbox['y1'], image_height)),
        'x2': max(0, min(bbox['x2'], image_width)),
        'y2': max(0, min(bbox['y2'], image_height)),
    }
