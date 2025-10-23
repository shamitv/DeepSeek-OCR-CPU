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
**Directory:** `2510.19670v1_enhanced_outputs/`  
**Demo Document:** [ENHANCED_PDF_DEMO_EXAMPLE.md](../ENHANCED_PDF_DEMO_EXAMPLE.md)

Example output from **enhanced PDF processing** (Phase 2 implementation), showing:
- ✨ Individual element extraction as separate images (289 elements)
- ✨ Element metadata JSON files with bounding boxes and metrics
- ✨ Type-specific visualization overlays (titles only, text only, all types colored)
- ✨ Raw model output with grounding references
- ✨ Image + caption association (automatic linking)
- ✨ Table extraction with captions and structure preservation
- ✨ Complex page handling (multiple images, tables, equations per page)
- All standard outputs (markdown, annotated images, etc.)

**Source:** "CoSense-LLM: Semantics-at-the-Edge" by Hasan Akgul et al. (arXiv 2510.19670v1, 19 pages, 289 elements)

**Highlights:**
- Page 6: Diagram with caption extraction
- Page 14: 2 charts + 2 tables with all captions
- Pages 13-16: Complex data visualization section

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

### Enhanced Output (`2510.19670v1_enhanced_outputs/`)
```
2510.19670v1_enhanced_outputs/
├── 2510.19670v1.md                # Combined markdown
├── document_structure.json        # NEW: Document metadata
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
├── page_0006/                     # Diagram with caption
│   ├── elements/
│   │   ├── page_0001_elem_0000_image.jpg
│   │   ├── page_0001_elem_0001_image_caption.jpg
│   │   └── ...
├── page_0014/                     # Charts + tables
│   ├── elements/
│   │   ├── page_0001_elem_0000_image.jpg        # Chart 1
│   │   ├── page_0001_elem_0001_image_caption.jpg
│   │   ├── page_0001_elem_0002_image.jpg        # Chart 2
│   │   ├── page_0001_elem_0007_table.jpg        # Table 1
│   │   ├── page_0001_elem_0008_table_caption.jpg
│   │   └── ...
│   └── images/
│       ├── 0.jpg                  # Chart extraction 1
│       └── 1.jpg                  # Chart extraction 2
└── ...
```

## Statistics

### Standard Output
- **Size:** ~15 MB
- **Pages:** 16
- **Elements:** Not individually extracted
- **Figures:** 2 extracted

### Enhanced Output
- **Size:** ~85 MB
- **Pages:** 19 (full document)
- **Elements:** 289 individually extracted
  - 201 text blocks
  - 58 subtitles
  - 8 images with captions
  - 3 tables with captions
  - 6 equations
  - 1 title
- **Element Images:** 289 JPG files
- **Metadata Files:** 289 JSON files
- **Overlays:** 76+ visualization images
- **Figures Extracted:** 8 (with automatic caption linking)

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
