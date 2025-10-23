# Examples Directory

This directory contains example outputs from the DeepSeek OCR CPU toolkit, demonstrating both standard and enhanced PDF processing capabilities.

## Contents

### Standard PDF Processing Output
**Directory:** `pdf_demo_output/`  
**Demo Document:** [PDF_DEMO_EXAMPLE.md](../PDF_DEMO_EXAMPLE.md)

Example output from standard PDF processing, showing:
- Combined markdown output
- Per-page OCR results
- Annotated images with bounding boxes
- Extracted figure images

**Source:** "The Standard Model of the Retina" by Markus Meister (arXiv 2510.17820v1, 16 pages)

### Enhanced PDF Processing Output
**Directory:** `enhanced_pdf_demo_output/`  
**Demo Document:** [ENHANCED_PDF_DEMO_EXAMPLE.md](../ENHANCED_PDF_DEMO_EXAMPLE.md)

Example output from **enhanced PDF processing** (Phase 2 implementation), showing:
- ✨ Individual element extraction as separate images
- ✨ Element metadata JSON files with bounding boxes and metrics
- ✨ Type-specific visualization overlays (titles only, text only, all types colored)
- ✨ Raw model output with grounding references
- All standard outputs (markdown, annotated images, etc.)

**Source:** "Semi-analytical pricing of American options with hybrid dividends" by Andrey Itkin (arXiv 2510.18159v1, 4 pages processed)

## Output Structure Comparison

### Standard Output (`pdf_demo_output/`)
```
pdf_demo_output/
├── document.md                    # Combined markdown
├── pages/                         # Page images
├── page_0001/
│   ├── result.mmd                 # Page markdown
│   ├── result_with_boxes.jpg      # Annotated image
│   └── images/                    # Extracted figures
└── ...
```

### Enhanced Output (`enhanced_pdf_demo_output/`)
```
enhanced_pdf_demo_output/
├── pages/                         # Page images
├── page_0001/
│   ├── result.mmd                 # Page markdown
│   ├── result_raw.txt             # ✨ NEW: Raw model output
│   ├── result_with_boxes.jpg      # Annotated image
│   ├── elements/                  # ✨ NEW: Individual elements
│   │   ├── page_0001_elem_0000_title.jpg
│   │   ├── page_0001_elem_0000_title.json
│   │   ├── page_0001_elem_0001_text.jpg
│   │   ├── page_0001_elem_0001_text.json
│   │   └── ...
│   ├── overlays/                  # ✨ NEW: Type-specific visualizations
│   │   ├── title_only.jpg
│   │   ├── text_only.jpg
│   │   ├── all_types_colored.jpg
│   │   └── ...
│   └── images/                    # Extracted figures
└── ...
```

## Statistics

### Standard Output
- **Size:** ~15 MB
- **Pages:** 16
- **Elements:** Not individually extracted
- **Figures:** 2 extracted

### Enhanced Output
- **Size:** ~28 MB (includes individual element images)
- **Pages:** 4 (partial document)
- **Elements:** 22 individually extracted (1 title, 1 subtitle, 20 text blocks)
- **Element Images:** 22 JPG files
- **Metadata Files:** 22 JSON files
- **Overlays per Page:** 4 visualization images

## Usage

To generate similar outputs:

### Standard Processing
```bash
python pdf_demo.py
```

### Enhanced Processing
```bash
python pdf_demo_enhanced.py
```

### Programmatic API
```python
# Standard
from inference import process_pdf
result = process_pdf("document.pdf", output_dir="output/")

# Enhanced
from inference import process_pdf_enhanced
result = process_pdf_enhanced(
    pdf_path="document.pdf",
    output_dir="output/",
    generate_overlays=True,
    save_elements=True,
)
```

## Documentation

- [PDF Demo Example](../PDF_DEMO_EXAMPLE.md) - Standard processing walkthrough
- [Enhanced PDF Demo Example](../ENHANCED_PDF_DEMO_EXAMPLE.md) - Enhanced processing walkthrough
- [PDF Processing Guide](../PDF_PROCESSING_GUIDE.md) - Comprehensive guide
- [Enhanced Extraction Quickstart](../ENHANCED_EXTRACTION_QUICKSTART.md) - Quick start guide
- [Implementation Summary](../reference/IMPLEMENTATION_SUMMARY.md) - Technical details

## Notes

- Enhanced output includes all standard output plus additional element extraction artifacts
- Element images and metadata enable fine-grained document analysis
- Type-specific overlays facilitate visual inspection and debugging
- Both standard and enhanced APIs maintain backward compatibility
