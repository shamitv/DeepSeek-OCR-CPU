# Enhanced Extraction Quick Start

## Installation

No additional installation needed if you already have the base environment set up.

```bash
# Ensure environment is activated
source .venv/bin/activate
```

## Basic Usage

### Process a Single Image

```python
from inference import process_image_enhanced

result = process_image_enhanced(
    image_path="page.png",
    output_dir="output/",
    generate_overlays=True,
    save_elements=True,
)

print(f"Extracted {len(result['elements'])} elements")
```

### Process a PDF

```python
from inference import process_pdf_enhanced

result = process_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
)

print(f"Processed {result['structure']['document_metadata']['num_pages']} pages")
print(f"Total elements: {result['structure']['document_metadata']['total_elements']}")
```

## What You Get

### 1. Individual Element Images
Each detected element (title, paragraph, image, table, etc.) is saved as:
- `elements/page_XXXX_elem_XXXX_TYPE.jpg` - Cropped image
- `elements/page_XXXX_elem_XXXX_TYPE.json` - Metadata

### 2. Type-Specific Overlays
Visualization overlays showing bounding boxes by type:
- `overlays/title_only.jpg`
- `overlays/paragraph_only.jpg`
- `overlays/image_only.jpg`
- `overlays/table_only.jpg`
- `overlays/all_types_colored.jpg`

### 3. Structured Data
- `elements.json` - All element metadata per page
- `document_structure.json` - Document-level structure

### 4. Raw Model Output
- `result_raw.txt` - Raw output with grounding references

## Query Examples

### Find All Images

```python
images = []
for page in result['pages']:
    images.extend([e for e in page['elements'] if e['type'] == 'image'])

for img in images:
    print(f"Image on page {img['page']}: {img['metrics']['width']}x{img['metrics']['height']}")
```

### Count Elements by Type

```python
from collections import Counter

all_elements = []
for page in result['pages']:
    all_elements.extend(page['elements'])

type_counts = Counter(e['type'] for e in all_elements)
print(dict(type_counts))
```

### Get Elements on Specific Page

```python
page_3_elements = [e for page in result['pages'] 
                   if page['page_number'] == 3
                   for e in page['elements']]
```

### Find Large Elements

```python
large_elements = [e for e in all_elements 
                  if e['metrics']['area'] > 50000]
```

## Demo Scripts

### Test Single Page
```bash
python3 test_single_page_enhanced.py
```

### Process Full PDF
```bash
python3 pdf_demo_enhanced.py
```

## Configuration Options

### Extraction Options

```python
extract_options = {
    'padding': 5,          # Pixels to add around elements
    'min_width': 10,       # Minimum element width
    'min_height': 10,      # Minimum element height
    'validate_strict': False,  # Reject invalid bboxes
}

result = process_image_enhanced(
    image_path="page.png",
    output_dir="output/",
    extract_options=extract_options,
)
```

## Element Data Structure

```python
{
    'id': 'page_0001_elem_0000',
    'type': 'title',
    'page': 1,
    'index': 0,
    'bounding_boxes': [
        {'x1': 100, 'y1': 50, 'x2': 600, 'y2': 100}
    ],
    'bounding_boxes_normalized': [
        {'x1': 0.059, 'y1': 0.023, 'x2': 0.353, 'y2': 0.045}
    ],
    'metrics': {
        'num_boxes': 1,
        'total_area': 25000,
        'width': 500,
        'height': 50,
        'aspect_ratio': 10.0,
    },
    'image_dimensions': {'width': 1700, 'height': 2200},
}
```

## Common Element Types

- `title` - Headings and titles
- `paragraph` - Text paragraphs
- `image` - Figures, diagrams, photos
- `table` - Tables
- `caption` - Image/table captions
- `equation` - Mathematical equations
- `list` - Lists
- `header` - Page headers
- `footer` - Page footers

## Tips

1. **Storage:** Enhanced extraction generates many files. Ensure sufficient disk space.

2. **Memory:** Each page loads the full image into memory. For large PDFs, process in batches.

3. **Performance:** Element extraction adds ~10-20% overhead compared to basic processing.

4. **Validation:** Check `result_raw.txt` to see actual grounding references detected.

## Troubleshooting

### No elements extracted
- Check if `result_raw.txt` exists and contains `<|ref|>` tags
- Verify model is saving raw output correctly

### Missing element images
- Check `elements/` directory was created
- Verify `save_elements=True` in function call

### No overlays generated
- Check `overlays/` directory exists
- Verify `generate_overlays=True` in function call

## Next Steps

See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for:
- Detailed API documentation
- Implementation details
- Future enhancements
- Complete feature list
