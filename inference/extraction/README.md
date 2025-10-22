# Enhanced Extraction Modules

This directory contains the enhanced extraction functionality for DeepSeek OCR.

## Modules

### `element_extractor.py`
Core extraction engine that parses grounding references from model output and extracts individual elements with metadata.

**Key Functions:**
- `extract_all_elements()` - Extract all elements from model output
- `parse_grounding_references()` - Parse grounding tags
- `extract_element_content()` - Extract element image region

### `bbox_processor.py`
Bounding box utilities for coordinate transformations, validation, and geometric operations.

**Key Functions:**
- `denormalize_bbox_999()` - Convert DeepSeek coords (0-999) to pixels
- `validate_bbox()` - Validate bounding box
- `calculate_bbox_metrics()` - Calculate width, height, area, aspect ratio
- `check_overlap()` - Calculate IoU between boxes

### `image_cropper.py`
Save individual element images with metadata JSON files.

**Key Functions:**
- `crop_and_save_element()` - Save single element
- `save_all_elements()` - Batch save all elements

### `overlay_generator.py`
Generate type-specific bounding box visualization overlays.

**Key Functions:**
- `generate_type_overlays()` - Create overlays for each element type
- `generate_type_overlay()` - Create overlay for specific type
- `generate_all_types_overlay()` - Color-coded overlay with all types

## Usage

```python
from inference.extraction import (
    extract_all_elements,
    save_all_elements,
    generate_type_overlays,
)

# Extract elements
elements = extract_all_elements(image, model_output, page_number=1)

# Save individual images
save_all_elements(image, elements, output_dir)

# Generate overlays
generate_type_overlays(image, elements, overlays_dir)
```

See `IMPLEMENTATION_SUMMARY.md` for detailed documentation.
