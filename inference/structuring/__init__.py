"""
Structuring module for DeepSeek OCR enhancements.

This module provides tools for building structured JSON representations
of document content, including element classification, hierarchy detection,
and relationship building.
"""

__version__ = "0.1.0"

from .json_builder import build_document_json
from .element_classifier import enrich_element
from .hierarchy_analyzer import build_document_hierarchy

__all__ = [
    "build_document_json",
    "enrich_element",
    "build_document_hierarchy",
]
