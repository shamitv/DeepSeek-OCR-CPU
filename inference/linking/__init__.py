"""
Linking module for DeepSeek OCR enhancements.

This module provides tools for linking extracted elements with their
document context, building manifests, resolving references, and
creating search indices.
"""

__version__ = "0.1.0"

from .manifest_builder import build_image_manifest
from .context_extractor import extract_element_context
from .reference_resolver import resolve_references
from .search_indexer import build_search_index

__all__ = [
    "build_image_manifest",
    "extract_element_context",
    "resolve_references",
    "build_search_index",
]
