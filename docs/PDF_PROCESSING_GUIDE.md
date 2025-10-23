# PDF Processing Guide

Complete guide to end-to-end PDF processing with DeepSeek OCR on CPU.

## Table of Contents
- [Overview](#overview)
- [Processing Pipeline](#processing-pipeline)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Workflow](#detailed-workflow)
- [Output Structure](#output-structure)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Overview

The DeepSeek OCR CPU toolkit provides a complete pipeline for processing PDF documents without requiring GPU acceleration. The system converts each PDF page to images, performs OCR independently on each page, extracts embedded figures, and combines results into a single markdown document.

### Key Features
- **CPU-only inference** - No CUDA or GPU required
- **Per-page processing** - Each page processed independently for memory efficiency
- **Figure extraction** - Automatically identifies and extracts embedded images
- **Structure preservation** - Maintains document hierarchy, equations, tables, and formatting
- **Bounding box visualization** - Optional annotated output showing detected regions
- **Markdown output** - Clean, structured markdown suitable for documentation or analysis

## Processing Pipeline

```
PDF Document
    ↓
[1] PDF → Images (PyMuPDF)
    │   - Converts each page to PNG at 200 DPI
    │   - Saves to pages/ subdirectory
    ↓
[2] Image Processing (per page)
    │   - Loads DeepSeek OCR model
    │   - Applies grounding-based OCR
    │   - Extracts text, structure, and figures
    ↓
[3] Result Aggregation
    │   - Combines per-page markdown
    │   - Inserts page markers
    │   - Saves combined output
    ↓
Final Markdown + Extracted Figures
```

## Prerequisites

Before processing PDFs, ensure the environment is set up:

1. **Python 3.12** (tested, other 3.x versions may work)
2. **CPU-optimized environment** installed via setup script
3. **DeepSeek OCR model** downloaded locally

### Setup Verification

```bash
# Check if virtual environment exists
ls -la .venv/

# Check if model is downloaded
ls -la model_data/deepseek-ai/DeepSeek-OCR/

# Check if setup is complete
source .venv/bin/activate
python -c "from inference import process_pdf; print('Setup OK')"
```

If any checks fail, run the setup script:

```bash
bash setup/setup_cpu_env.sh
```

## Quick Start

### Process a Single PDF

```bash
# Activate the virtual environment
source .venv/bin/activate

# Process a PDF using the demo script
python pdf_demo.py
```

This processes the first PDF found in `test_files/pdf/` and saves results to `test_files/pdf/<filename>_outputs/`.

### Process a Custom PDF

```python
from inference import process_pdf

# Process with auto-generated output directory
result = process_pdf("path/to/document.pdf")

# Process with custom output directory
result = process_pdf(
    pdf_path="path/to/document.pdf",
    output_dir="path/to/output"
)

print(result)  # Combined markdown text
```

## Detailed Workflow

### Step 1: PDF to Images Conversion

The pipeline uses PyMuPDF (fitz) to convert each PDF page to a high-resolution PNG image.

**Location:** `inference/pdf_to_images.py`

**Parameters:**
- `dpi`: Resolution for rendering (default: 200)
- `image_format`: Output format (default: "png")

**Process:**
1. Opens PDF document with PyMuPDF
2. Iterates through each page
3. Renders page at specified DPI using transformation matrix
4. Ensures consistent RGB color space (removes alpha channel)
5. Saves to `pages/page_XXXX.png`

**Code example:**

```python
from inference.pdf_to_images import pdf_to_images

image_paths = pdf_to_images(
    pdf_path="document.pdf",
    output_dir="output/pages",
    dpi=200,
    image_format="png"
)
# Returns: ['output/pages/page_0001.png', 'output/pages/page_0002.png', ...]
```

### Step 2: Image OCR Processing

Each rendered page image is processed independently by the DeepSeek OCR model.

**Location:** `inference/image.py`

**Model Configuration:**
- `base_size`: 1024 (base resolution for processing)
- `image_size`: 640 (target size for vision encoder)
- `crop_mode`: True (enables intelligent cropping)
- `test_compress`: True (enables compression for efficiency)

**Process:**
1. Loads model and tokenizer (cached after first load)
2. Constructs grounding prompt: `"<image>\n<|grounding|>Convert the document to markdown."`
3. Runs model inference on the image
4. Saves results to page-specific output directory:
   - `result.mmd` - Extracted markdown text
   - `result_with_boxes.jpg` - Annotated image with bounding boxes (if enabled)
   - `images/` - Extracted figure images (numbered sequentially)

**Code example:**

```python
from inference.image import process_image

markdown_text = process_image(
    image_path="pages/page_0001.png",
    output_dir="output/page_0001"
)
```

### Step 3: Result Aggregation

After processing all pages, the markdown results are combined into a single document.

**Location:** `inference/pdf.py`

**Process:**
1. Collects markdown text from each page
2. Inserts page markers: `<!-- Page N -->`
3. Joins pages with double newlines for proper spacing
4. Saves combined markdown as `<pdf_name>.md`

**Page marker format:**
```markdown
<!-- Page 1 -->
[Page 1 content...]

<!-- Page 2 -->
[Page 2 content...]
```

## Output Structure

When processing `document.pdf`, the following directory structure is created:

```
document_outputs/
├── document.md                    # Combined markdown for all pages
├── pages/                         # Rendered page images (intermediate)
│   ├── page_0001.png
│   ├── page_0002.png
│   ├── page_0003.png
│   └── ...
├── page_0001/                     # First page results
│   ├── result.mmd                 # Page 1 markdown
│   ├── result_with_boxes.jpg      # Annotated page (optional)
│   └── images/                    # Figures from page 1
│       ├── 0.jpg
│       └── 1.jpg
├── page_0002/                     # Second page results
│   ├── result.mmd
│   ├── result_with_boxes.jpg
│   └── images/
│       └── 0.jpg
└── ...
```

### Output Files

| File | Description |
|------|-------------|
| `document.md` | Combined markdown from all pages with page markers |
| `pages/page_XXXX.png` | High-resolution rendering of each PDF page (200 DPI) |
| `page_XXXX/result.mmd` | Per-page markdown output from OCR |
| `page_XXXX/result_with_boxes.jpg` | Visual annotation showing detected text regions and bounding boxes |
| `page_XXXX/images/*.jpg` | Figures, diagrams, and images extracted from the page |

## Configuration Options

### Adjusting Resolution

Higher DPI produces better OCR accuracy but increases processing time and memory usage:

```python
from inference.pdf_to_images import pdf_to_images

# Low resolution (faster, less accurate)
pdf_to_images("doc.pdf", "output", dpi=150)

# Standard resolution (recommended)
pdf_to_images("doc.pdf", "output", dpi=200)

# High resolution (slower, more accurate)
pdf_to_images("doc.pdf", "output", dpi=300)
```

### Custom Output Directory

Control where results are saved:

```python
from inference import process_pdf

# Auto-generated output directory (default)
# Creates: /path/to/document_outputs/
process_pdf("/path/to/document.pdf")

# Custom output directory
process_pdf(
    pdf_path="/path/to/document.pdf",
    output_dir="/custom/output/location"
)
```

### Processing Specific Pages

To process only specific pages, convert them to images first:

```python
from pathlib import Path
import fitz
from inference.image import process_image

# Extract only pages 5-10
pdf = fitz.open("document.pdf")
for page_num in range(4, 10):  # 0-indexed
    page = pdf.load_page(page_num)
    pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
    image_path = f"page_{page_num+1:04d}.png"
    pix.save(image_path)
    
    markdown = process_image(image_path, f"output/page_{page_num+1:04d}")
    print(f"Page {page_num+1} processed")
```

## Troubleshooting

### Common Issues

#### Issue: "PDF file not found"

**Solution:** Ensure the path is correct and uses absolute paths or proper relative paths:

```python
from pathlib import Path

pdf_path = Path("document.pdf").expanduser().resolve()
process_pdf(str(pdf_path))
```

#### Issue: "No pages found in PDF"

**Cause:** PDF conversion failed or PDF is corrupted.

**Solution:**
1. Verify PDF is valid: `pdfinfo document.pdf`
2. Check PyMuPDF can open it:
   ```python
   import fitz
   doc = fitz.open("document.pdf")
   print(f"Pages: {doc.page_count}")
   ```
3. Try re-downloading or repairing the PDF

#### Issue: "Model inference did not return any output"

**Cause:** Model failed to process the image.

**Solution:**
1. Check image was created properly
2. Verify image is readable:
   ```python
   from PIL import Image
   img = Image.open("page_0001.png")
   print(img.size, img.mode)
   ```
3. Check available memory (model requires ~4-6 GB RAM)

#### Issue: Out of Memory

**Cause:** Processing large/complex pages or multiple pages concurrently.

**Solution:**
1. Process pages sequentially (already default behavior)
2. Reduce DPI: use 150 instead of 200
3. Close other applications to free memory
4. Use swap space if necessary

#### Issue: Poor OCR Quality

**Cause:** Low-quality PDF, complex layouts, or non-standard fonts.

**Solution:**
1. Increase DPI to 300 for better resolution
2. Check source PDF quality
3. Verify the page rendered correctly (inspect `pages/page_XXXX.png`)
4. For scanned documents, consider pre-processing (deskewing, contrast enhancement)

### Debug Mode

Enable verbose output to diagnose issues:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

from inference import process_pdf
result = process_pdf("document.pdf")
```

## Advanced Usage

### Batch Processing Multiple PDFs

```python
from pathlib import Path
from inference import process_pdf

pdf_dir = Path("documents")
for pdf_path in pdf_dir.glob("*.pdf"):
    print(f"Processing {pdf_path.name}...")
    try:
        result = process_pdf(str(pdf_path))
        print(f"✓ Completed {pdf_path.name}")
    except Exception as e:
        print(f"✗ Failed {pdf_path.name}: {e}")
```

### Custom Prompt

Modify the OCR prompt for specific extraction tasks:

```python
from inference.model_loader import load_model_and_tokenizer
from pathlib import Path

tokenizer, model = load_model_and_tokenizer()

# Custom prompt for extracting only tables
custom_prompt = "<image>\n<|grounding|>Extract all tables from this document in markdown format."

result = model.infer(
    tokenizer,
    prompt=custom_prompt,
    image_file="page_0001.png",
    output_path="output",
    base_size=1024,
    image_size=640,
    crop_mode=True,
    save_results=True,
    test_compress=True,
)
```

### Parallel Processing with Multiprocessing

**Warning:** Each process loads the full model (~4-6 GB). Ensure sufficient RAM.

```python
from multiprocessing import Pool
from pathlib import Path
from inference.image import process_image

def process_page(args):
    image_path, output_dir = args
    return process_image(image_path, output_dir)

# Prepare page list
pages = [(f"pages/page_{i:04d}.png", f"output/page_{i:04d}") 
         for i in range(1, 17)]

# Process with 2 workers (requires ~12 GB RAM)
with Pool(2) as pool:
    results = pool.map(process_page, pages)
```

### Integration with Document Management Systems

```python
from inference import process_pdf
import json

def process_and_index(pdf_path: str, metadata: dict) -> dict:
    """Process PDF and prepare for indexing."""
    markdown_text = process_pdf(pdf_path)
    
    return {
        "metadata": metadata,
        "content": markdown_text,
        "page_count": markdown_text.count("<!-- Page"),
        "has_figures": "![" in markdown_text,
        "has_equations": "$$" in markdown_text or "$" in markdown_text,
    }

# Example usage
result = process_and_index(
    "research_paper.pdf",
    metadata={
        "title": "DeepSeek OCR Research",
        "author": "Author Name",
        "date": "2025-10-22"
    }
)

# Save to index
with open("index.json", "w") as f:
    json.dump(result, f, indent=2)
```

### Export to Other Formats

Convert the markdown output to other formats using pandoc:

```bash
# Install pandoc
sudo apt install pandoc

# Convert to HTML
pandoc document.md -o document.html

# Convert to Word
pandoc document.md -o document.docx

# Convert to LaTeX
pandoc document.md -o document.tex
```

## Performance Benchmarks

Typical processing times on Intel i5 CPU (4 cores, 16GB RAM):

| Document Type | Pages | Resolution | Time per Page | Total Time |
|--------------|-------|------------|---------------|------------|
| Research paper | 16 | 200 DPI | ~45-60s | ~12-15 min |
| Technical manual | 50 | 200 DPI | ~45-60s | ~40-50 min |
| Simple text | 10 | 150 DPI | ~30-40s | ~5-7 min |

**Factors affecting performance:**
- CPU speed and core count
- Available RAM
- Document complexity (figures, equations, tables)
- PDF resolution
- Page size and layout

## Best Practices

1. **Test on sample pages first** - Process 1-2 pages to verify output quality before processing large documents

2. **Use appropriate DPI** - 200 DPI is optimal for most documents; use 150 for speed, 300 for accuracy

3. **Monitor memory usage** - Each page requires ~4-6 GB during processing

4. **Check intermediate outputs** - Verify `pages/*.png` images are clean and readable

5. **Preserve original PDFs** - Keep original files; processing is non-destructive

6. **Version control outputs** - Track changes to markdown outputs for documentation

7. **Validate results** - Review `result_with_boxes.jpg` to ensure proper text detection

8. **Handle errors gracefully** - Implement retry logic and logging for production use

## Related Documentation

- [PDF Demo Example](PDF_DEMO_EXAMPLE.md) - Complete example with 16-page research paper
- [README.md](../README.md) - Main project documentation and setup
- [Image Processing](../inference/image.py) - Single image OCR details
- [Model Configuration](../model_data/deepseek-ai/DeepSeek-OCR/config.json) - Model parameters

## Support and Contributing

For issues, questions, or contributions:
- Check existing documentation in `docs/`
- Review code in `inference/` directory
- Examine test files in `test_files/pdf/` for examples
- Refer to original DeepSeek OCR documentation in `README-source.md`

---

**Last Updated:** October 22, 2025  
**Version:** 1.0
