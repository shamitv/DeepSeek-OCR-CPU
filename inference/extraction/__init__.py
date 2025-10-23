"""
Extraction module for DeepSeek OCR enhancements.

This module provides tools for extracting individual elements from OCR output,
including bounding boxes, element metadata, and type-specific overlays.
"""

__version__ = "0.1.0"

from .element_extractor import extract_all_elements, extract_element_content
from .bbox_processor import (
    normalize_bbox,
    denormalize_bbox,
    denormalize_bbox_999,
    validate_bbox,
    add_padding,
    calculate_bbox_metrics,
    check_overlap,
)
from .image_cropper import crop_and_save_element, save_all_elements
from .overlay_generator import generate_type_overlays, generate_type_overlay

__all__ = [
    "extract_all_elements",
    "extract_element_content",
    "normalize_bbox",
    "denormalize_bbox",
    "denormalize_bbox_999",
    "validate_bbox",
    "add_padding",
    "calculate_bbox_metrics",
    "check_overlap",
    "crop_and_save_element",
    "save_all_elements",
    "generate_type_overlays",
    "generate_type_overlay",
]
