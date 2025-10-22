# PDF Extraction Enhancement Plan

**Version:** 1.0  
**Created:** October 22, 2025  
**Status:** Planning  
**Target:** Q1 2026

## Executive Summary

This plan outlines enhancements to the DeepSeek OCR CPU toolkit's PDF extraction capabilities, moving beyond basic markdown output to provide:

1. **Structured JSON output** with typed document elements (tables, paragraphs, images, equations, etc.)
2. **Individual bounding box extraction** as separate image files with metadata
3. **Data-image linking** to correlate extracted images with their semantic context in the document structure

These enhancements will enable:
- Better downstream processing and analysis
- Integration with document management systems
- Enhanced search and retrieval capabilities
- Fine-grained document understanding

---

## Current State Analysis

### Existing Capabilities

**Current Output:**
- ✅ Combined markdown file (`.md`) for all pages
- ✅ Per-page markdown files (`result.mmd`)
- ✅ Annotated images with all bounding boxes (`result_with_boxes.jpg`)
- ✅ Extracted figure images (only `label_type == 'image'`)

**Current Processing Flow:**
```
PDF → Images → OCR Model → Markdown Text + Grounding Data
                                ↓
                     Extract figures (type='image')
                                ↓
                     Draw all boxes on single image
```

**Grounding Data Structure:**
```python
# Format: <|ref|>{label_type}<|/ref|><|det|>{coordinates}<|/det|>
# Example: <|ref|>paragraph<|/ref|><|det|>[[x1, y1, x2, y2], ...]<|/det|>

# Existing label types detected:
- 'image'       # Figures, diagrams, photos
- 'paragraph'   # Text paragraphs
- 'title'       # Headings and titles
- 'table'       # Tables (possibly)
- (other types to be discovered)
```

**Model Output Processing:**
```python
# In modeling_deepseekocr.py line ~970-1000
matches_ref, matches_images, mathes_other = re_match(outputs)
# matches_ref: all <|ref|>...<|/ref|><|det|>...<|/det|> patterns
# matches_images: only type='image'
# mathes_other: all other types

# Current extraction (line ~112-118):
if label_type == 'image':
    cropped = image.crop((x1, y1, x2, y2))
    cropped.save(f"{output_path}/images/{img_idx}.jpg")
```

### Current Limitations

1. **No Structured Output**
   - Markdown is unstructured text
   - No machine-readable document hierarchy
   - Difficult to programmatically query elements
   - No type information for downstream processing

2. **Limited Image Extraction**
   - Only extracts `label_type == 'image'`
   - Other element types (paragraphs, titles, tables) not extracted as images
   - No way to extract specific regions for analysis
   - Loses fine-grained spatial information

3. **No Data-Image Linking**
   - Extracted images have numeric names (`0.jpg`, `1.jpg`)
   - No metadata connecting image to document context
   - Can't trace which paragraph/section an image belongs to
   - No bounding box information preserved for extracted images

4. **Single Annotated Image**
   - All bounding boxes overlaid on one image
   - Cluttered for complex pages
   - Can't view individual element types separately
   - No granular extraction capability

---

## Enhancement Objectives

### 1. Structured JSON Information

**Goal:** Provide a machine-readable, hierarchical representation of document structure with typed elements.

**Benefits:**
- Enable programmatic document analysis
- Support advanced search and retrieval
- Facilitate integration with databases and systems
- Preserve semantic relationships
- Enable element-level processing

**Target JSON Schema:**
```json
{
  "document_metadata": {
    "source_pdf": "document.pdf",
    "total_pages": 16,
    "processing_date": "2025-10-22T10:30:00Z",
    "model_version": "DeepSeek-OCR-CPU-v1.0",
    "resolution_dpi": 200
  },
  "pages": [
    {
      "page_number": 1,
      "image_path": "pages/page_0001.png",
      "dimensions": {
        "width": 1654,
        "height": 2339
      },
      "elements": [
        {
          "id": "page_1_elem_0",
          "type": "title",
          "bounding_box": {
            "x1": 150,
            "y1": 200,
            "x2": 1500,
            "y2": 280,
            "normalized": {
              "x1": 0.091,
              "y1": 0.085,
              "x2": 0.907,
              "y2": 0.120
            }
          },
          "content": {
            "text": "The Standard Model of the Retina",
            "markdown": "# The Standard Model of the Retina"
          },
          "extracted_image": "page_0001/elements/elem_0_title.jpg",
          "confidence": 0.98,
          "metadata": {
            "font_size_estimated": "large",
            "alignment": "center"
          }
        },
        {
          "id": "page_1_elem_1",
          "type": "paragraph",
          "bounding_box": {
            "x1": 200,
            "y1": 350,
            "x2": 1450,
            "y2": 580,
            "normalized": {
              "x1": 0.121,
              "y1": 0.150,
              "x2": 0.877,
              "y2": 0.248
            }
          },
          "content": {
            "text": "The retina is a complex neural circuit...",
            "markdown": "The retina is a complex neural circuit...",
            "word_count": 145
          },
          "extracted_image": "page_0001/elements/elem_1_paragraph.jpg",
          "relationships": {
            "parent": "page_1_elem_0",
            "follows": "page_1_elem_0"
          }
        },
        {
          "id": "page_1_elem_2",
          "type": "image",
          "bounding_box": {
            "x1": 300,
            "y1": 650,
            "x2": 1350,
            "y2": 1450,
            "normalized": {
              "x1": 0.181,
              "y1": 0.278,
              "x2": 0.816,
              "y2": 0.620
            }
          },
          "content": {
            "caption": "Figure 1: Schematic of retinal layers",
            "markdown": "![Figure 1: Schematic of retinal layers](images/0.jpg)",
            "original_ref": "<|ref|>image<|/ref|><|det|>[[300, 650, 1350, 1450]]<|/det|>"
          },
          "extracted_image": "page_0001/elements/elem_2_image.jpg",
          "metadata": {
            "figure_number": 1,
            "has_caption": true,
            "image_type": "diagram"
          }
        },
        {
          "id": "page_1_elem_3",
          "type": "table",
          "bounding_box": {
            "x1": 200,
            "y1": 1550,
            "x2": 1450,
            "y2": 1950,
            "normalized": {
              "x1": 0.121,
              "y1": 0.663,
              "x2": 0.877,
              "y2": 0.834
            }
          },
          "content": {
            "markdown": "| Cell Type | Count | ... |\n|-----------|-------|-----|\n| ...",
            "parsed_table": {
              "headers": ["Cell Type", "Count"],
              "rows": [
                ["Photoreceptors", "120M"],
                ["Bipolar cells", "15M"]
              ]
            }
          },
          "extracted_image": "page_0001/elements/elem_3_table.jpg",
          "metadata": {
            "row_count": 5,
            "column_count": 3
          }
        },
        {
          "id": "page_1_elem_4",
          "type": "equation",
          "bounding_box": {
            "x1": 600,
            "y1": 2000,
            "x2": 1050,
            "y2": 2100,
            "normalized": {
              "x1": 0.363,
              "y1": 0.855,
              "x2": 0.635,
              "y2": 0.898
            }
          },
          "content": {
            "latex": "E = mc^2",
            "markdown": "$$E = mc^2$$"
          },
          "extracted_image": "page_0001/elements/elem_4_equation.jpg",
          "metadata": {
            "equation_type": "inline"
          }
        }
      ],
      "element_count": {
        "title": 1,
        "paragraph": 8,
        "image": 2,
        "table": 1,
        "equation": 3,
        "total": 15
      }
    }
  ],
  "document_statistics": {
    "total_elements": 240,
    "element_distribution": {
      "title": 16,
      "paragraph": 180,
      "image": 25,
      "table": 12,
      "equation": 7
    }
  }
}
```

### 2. Individual Bounding Box Extraction

**Goal:** Extract every detected element as a separate image file with associated metadata.

**Benefits:**
- Fine-grained element-level analysis
- Training data generation for ML models
- Individual element quality assessment
- Flexible post-processing workflows
- Element-specific enhancement (OCR re-run, super-resolution, etc.)

**Target Output Structure:**
```
page_0001/
├── result.mmd                          # Current markdown output
├── result_with_boxes.jpg                # Current annotated image
├── elements/                            # NEW: Individual elements
│   ├── elem_0_title.jpg                # Extracted title region
│   ├── elem_0_title.json               # Element metadata
│   ├── elem_1_paragraph.jpg            # Extracted paragraph region
│   ├── elem_1_paragraph.json
│   ├── elem_2_image.jpg                # Figure/diagram
│   ├── elem_2_image.json
│   ├── elem_3_table.jpg                # Table region
│   ├── elem_3_table.json
│   ├── elem_4_equation.jpg             # Equation region
│   ├── elem_4_equation.json
│   └── ...
├── overlays/                            # NEW: Type-specific overlays
│   ├── titles_only.jpg                 # Only title boxes
│   ├── paragraphs_only.jpg             # Only paragraph boxes
│   ├── images_only.jpg                 # Only image boxes
│   ├── tables_only.jpg                 # Only table boxes
│   └── equations_only.jpg              # Only equation boxes
└── images/                              # Current figure extraction
    ├── 0.jpg
    └── 1.jpg
```

**Per-Element Metadata JSON:**
```json
{
  "element_id": "page_1_elem_2",
  "type": "image",
  "page": 1,
  "bounding_box": {
    "absolute": {"x1": 300, "y1": 650, "x2": 1350, "y2": 1450},
    "normalized": {"x1": 0.181, "y1": 0.278, "x2": 0.816, "y2": 0.620}
  },
  "dimensions": {
    "width": 1050,
    "height": 800,
    "aspect_ratio": 1.3125
  },
  "content": {
    "text": "Figure 1: Schematic of retinal layers",
    "markdown": "![Figure 1](images/0.jpg)"
  },
  "file_references": {
    "extracted_image": "elem_2_image.jpg",
    "source_page": "../pages/page_0001.png",
    "in_combined_doc": "images/0.jpg"
  },
  "extraction_metadata": {
    "timestamp": "2025-10-22T10:30:15Z",
    "model_confidence": 0.95,
    "color_space": "RGB"
  }
}
```

### 3. Data-Image Linking

**Goal:** Create robust connections between extracted visual elements and their semantic context in the document.

**Benefits:**
- Trace images back to source context
- Enable contextual search ("find all images in section 3")
- Support citation and reference management
- Facilitate document restructuring
- Enable intelligent document querying

**Linking Mechanisms:**

#### A. Image Manifest
```json
{
  "document": "document.pdf",
  "image_manifest": [
    {
      "image_id": "img_0",
      "current_path": "page_0001/images/0.jpg",
      "element_id": "page_1_elem_2",
      "type": "image",
      "caption": "Figure 1: Schematic of retinal layers",
      "page": 1,
      "bounding_box": {"x1": 300, "y1": 650, "x2": 1350, "y2": 1450},
      "context": {
        "preceding_text": "The structure consists of multiple layers...",
        "following_text": "As shown in the figure, the photoreceptors...",
        "section": "Introduction",
        "section_hierarchy": ["Introduction", "Retinal Structure"]
      },
      "references": {
        "referenced_in_pages": [1, 3, 5],
        "related_elements": ["page_1_elem_1", "page_1_elem_3"]
      }
    },
    {
      "image_id": "img_1",
      "current_path": "page_0002/images/0.jpg",
      "element_id": "page_2_elem_5",
      "type": "image",
      "caption": "Figure 2: Signal propagation pathways",
      "page": 2,
      "bounding_box": {"x1": 250, "y1": 400, "x2": 1400, "y2": 1200},
      "context": {
        "preceding_text": "Signal processing occurs through...",
        "following_text": "This pathway enables...",
        "section": "Signal Processing"
      }
    }
  ]
}
```

#### B. Element Graph
```json
{
  "document_graph": {
    "nodes": [
      {
        "id": "page_1_elem_0",
        "type": "title",
        "content": "The Standard Model of the Retina",
        "level": 1
      },
      {
        "id": "page_1_elem_1",
        "type": "paragraph",
        "content_preview": "The retina is a complex...",
        "has_images": false
      },
      {
        "id": "page_1_elem_2",
        "type": "image",
        "image_path": "page_0001/elements/elem_2_image.jpg",
        "caption": "Figure 1: Schematic"
      }
    ],
    "edges": [
      {
        "source": "page_1_elem_0",
        "target": "page_1_elem_1",
        "relationship": "contains"
      },
      {
        "source": "page_1_elem_1",
        "target": "page_1_elem_2",
        "relationship": "references"
      },
      {
        "source": "page_1_elem_2",
        "target": "page_1_elem_3",
        "relationship": "precedes"
      }
    ]
  }
}
```

#### C. Search Index
```json
{
  "search_index": {
    "by_type": {
      "image": ["page_1_elem_2", "page_2_elem_5", "page_3_elem_1"],
      "table": ["page_1_elem_3", "page_4_elem_2"],
      "equation": ["page_1_elem_4", "page_2_elem_8"]
    },
    "by_page": {
      "1": ["page_1_elem_0", "page_1_elem_1", "page_1_elem_2"],
      "2": ["page_2_elem_0", "page_2_elem_1"]
    },
    "by_keyword": {
      "retina": ["page_1_elem_0", "page_1_elem_1", "page_2_elem_3"],
      "figure": ["page_1_elem_2", "page_2_elem_5"]
    }
  }
}
```

---

## Technical Implementation Plan

### Phase 1: Foundation (Weeks 1-2)

#### 1.1 Model Output Analysis
**Objective:** Understand all possible label types and grounding data structures.

**Tasks:**
- [ ] Run OCR on diverse document types (research papers, textbooks, forms)
- [ ] Collect and catalog all `label_type` values encountered
- [ ] Document coordinate format and edge cases
- [ ] Analyze multi-box elements (e.g., multi-column paragraphs)
- [ ] Test boundary conditions (overlapping boxes, nested elements)

**Deliverables:**
- `docs/reference/model_output_specification.md`
- Test dataset with annotated ground truth
- Label type taxonomy

#### 1.2 JSON Schema Design
**Objective:** Define robust, extensible schema for structured output.

**Tasks:**
- [ ] Design JSON schema following best practices
- [ ] Include version field for schema evolution
- [ ] Support optional fields for flexibility
- [ ] Enable extensions without breaking changes
- [ ] Create validation rules

**Deliverables:**
- `docs/schemas/document_structure_v1.json` (JSON Schema format)
- `docs/schemas/element_metadata_v1.json`
- `docs/schemas/image_manifest_v1.json`
- Schema validation utilities

#### 1.3 Module Structure Planning
**Objective:** Design clean, maintainable code architecture.

**Proposed Structure:**
```
inference/
├── __init__.py
├── image.py                    # Existing
├── pdf.py                      # Existing
├── model_loader.py             # Existing
├── pdf_to_images.py            # Existing
├── extraction/                 # NEW MODULE
│   ├── __init__.py
│   ├── element_extractor.py   # Extract individual elements
│   ├── bbox_processor.py      # Bounding box utilities
│   ├── image_cropper.py       # Crop and save element images
│   └── overlay_generator.py   # Generate type-specific overlays
├── structuring/                # NEW MODULE
│   ├── __init__.py
│   ├── json_builder.py        # Build structured JSON
│   ├── element_classifier.py  # Classify and enrich elements
│   ├── relationship_builder.py # Build element relationships
│   └── hierarchy_analyzer.py  # Detect document hierarchy
└── linking/                    # NEW MODULE
    ├── __init__.py
    ├── manifest_builder.py    # Build image manifest
    ├── context_extractor.py   # Extract surrounding context
    ├── reference_resolver.py  # Resolve cross-references
    └── search_indexer.py      # Build search indices
```

**Deliverables:**
- Module skeleton with stubs
- Interface documentation
- Integration points identified

### Phase 2: Core Extraction (Weeks 3-4)

#### 2.1 Element Extraction Engine
**File:** `inference/extraction/element_extractor.py`

**Core Function:**
```python
def extract_all_elements(
    image: Image.Image,
    grounding_refs: List[Tuple],
    output_dir: Path,
    extract_options: Optional[Dict] = None
) -> List[Dict]:
    """
    Extract all detected elements as individual images with metadata.
    
    Args:
        image: Source page image
        grounding_refs: List of (full_match, label_type, coordinates)
        output_dir: Output directory for extracted elements
        extract_options: Optional configuration
            - padding: pixels to add around bbox (default: 5)
            - min_size: minimum dimension to extract (default: 10)
            - format: output format (default: 'jpg')
            - quality: JPEG quality (default: 95)
    
    Returns:
        List of element dictionaries with paths and metadata
    """
```

**Implementation Steps:**
1. Parse grounding references (reuse existing `extract_coordinates_and_label`)
2. For each element:
   - Calculate bounding box in absolute coordinates
   - Add padding (optional)
   - Crop image region
   - Generate unique filename: `elem_{idx}_{type}.{ext}`
   - Save image file
   - Create metadata JSON
3. Handle errors gracefully (invalid coords, out of bounds)
4. Generate element summary

**Tasks:**
- [ ] Implement core extraction logic
- [ ] Add coordinate normalization (absolute ↔ normalized)
- [ ] Support padding and margin options
- [ ] Implement quality controls (min size, aspect ratio checks)
- [ ] Add progress reporting for large pages
- [ ] Write unit tests

#### 2.2 Bounding Box Processor
**File:** `inference/extraction/bbox_processor.py`

**Core Functions:**
```python
def normalize_bbox(bbox: Dict, image_width: int, image_height: int) -> Dict:
    """Convert absolute coordinates to normalized [0,1] range."""

def denormalize_bbox(bbox: Dict, image_width: int, image_height: int) -> Dict:
    """Convert normalized coordinates to absolute pixels."""

def validate_bbox(bbox: Dict, image_width: int, image_height: int) -> bool:
    """Check if bounding box is valid and within image bounds."""

def add_padding(bbox: Dict, padding: int, image_width: int, image_height: int) -> Dict:
    """Add padding around bbox, clipping to image bounds."""

def calculate_bbox_metrics(bbox: Dict) -> Dict:
    """Calculate width, height, area, aspect ratio."""

def check_overlap(bbox1: Dict, bbox2: Dict) -> float:
    """Calculate IoU (Intersection over Union) between two boxes."""
```

**Tasks:**
- [ ] Implement coordinate transformation utilities
- [ ] Add validation and error handling
- [ ] Support different coordinate formats (model uses 0-999 normalized)
- [ ] Add geometric operations (IoU, containment, etc.)
- [ ] Write comprehensive tests

#### 2.3 Overlay Generator
**File:** `inference/extraction/overlay_generator.py`

**Core Function:**
```python
def generate_type_overlays(
    image: Image.Image,
    elements: List[Dict],
    output_dir: Path
) -> Dict[str, str]:
    """
    Generate separate overlay images for each element type.
    
    Returns mapping: {"titles": "overlays/titles_only.jpg", ...}
    """
```

**Tasks:**
- [ ] Group elements by type
- [ ] Generate per-type overlays (reuse existing drawing logic)
- [ ] Use consistent color schemes per type
- [ ] Add legends/labels
- [ ] Save to `overlays/` subdirectory
- [ ] Generate combined overlay with type-specific colors

### Phase 3: Structured Output (Weeks 5-6)

#### 3.1 JSON Builder
**File:** `inference/structuring/json_builder.py`

**Core Function:**
```python
def build_document_json(
    pdf_path: str,
    pages_data: List[Dict],
    output_path: str
) -> Dict:
    """
    Build complete structured JSON representation.
    
    Args:
        pdf_path: Source PDF path
        pages_data: List of per-page extraction data
        output_path: Where to save JSON
    
    Returns:
        Complete document structure dictionary
    """
```

**Implementation:**
1. Build document metadata (source, dates, counts)
2. For each page:
   - Convert elements to JSON format
   - Add page-level metadata
   - Calculate statistics
3. Add document-level statistics
4. Validate against schema
5. Save formatted JSON

**Tasks:**
- [ ] Implement JSON construction pipeline
- [ ] Add schema validation
- [ ] Support incremental building (streaming)
- [ ] Handle large documents efficiently
- [ ] Add pretty-printing and compression options

#### 3.2 Element Classifier
**File:** `inference/structuring/element_classifier.py`

**Core Function:**
```python
def enrich_element(
    element: Dict,
    content: str,
    page_context: Dict
) -> Dict:
    """
    Add metadata and classification to element.
    
    Enrichments:
    - Confidence scores
    - Content analysis (word count, has equations, etc.)
    - Type-specific metadata (table rows/cols, equation complexity)
    - Reading order estimation
    """
```

**Tasks:**
- [ ] Implement type-specific analyzers
- [ ] Extract markdown features (tables, equations, lists)
- [ ] Estimate reading order (top-to-bottom, left-to-right)
- [ ] Detect semantic roles (caption, header, footer)
- [ ] Add confidence/quality metrics

#### 3.3 Hierarchy Analyzer
**File:** `inference/structuring/hierarchy_analyzer.py`

**Core Function:**
```python
def build_document_hierarchy(elements: List[Dict]) -> Dict:
    """
    Detect document structure (sections, subsections, etc.).
    
    Returns hierarchy tree with parent-child relationships.
    """
```

**Tasks:**
- [ ] Detect headings and hierarchy levels (H1, H2, H3)
- [ ] Group elements into sections
- [ ] Identify list structures
- [ ] Detect captions and their associated images/tables
- [ ] Build tree structure

### Phase 4: Linking System (Weeks 7-8)

#### 4.1 Manifest Builder
**File:** `inference/linking/manifest_builder.py`

**Core Function:**
```python
def build_image_manifest(
    document_structure: Dict,
    output_dir: Path
) -> Dict:
    """
    Create comprehensive image manifest with all links.
    """
```

**Tasks:**
- [ ] Extract all image elements
- [ ] Link to file paths
- [ ] Add context information
- [ ] Build cross-references
- [ ] Save manifest JSON

#### 4.2 Context Extractor
**File:** `inference/linking/context_extractor.py`

**Core Function:**
```python
def extract_element_context(
    element: Dict,
    all_elements: List[Dict],
    window_size: int = 2
) -> Dict:
    """
    Extract surrounding context for an element.
    
    Returns:
        - preceding_elements
        - following_elements
        - preceding_text (concatenated)
        - following_text (concatenated)
        - section_context
    """
```

**Tasks:**
- [ ] Implement context window extraction
- [ ] Handle page boundaries
- [ ] Extract section/chapter context
- [ ] Identify references in text ("see Figure 1")
- [ ] Build bidirectional links

#### 4.3 Reference Resolver
**File:** `inference/linking/reference_resolver.py`

**Core Function:**
```python
def resolve_references(
    document_structure: Dict
) -> Dict:
    """
    Find and resolve cross-references in the document.
    
    Detects patterns like:
    - "Figure 1", "Fig. 1", "figure 1"
    - "Table 2", "Tab. 2"
    - "Equation 3", "Eq. (3)"
    - "Section 2.1"
    """
```

**Tasks:**
- [ ] Implement reference pattern matching
- [ ] Link references to actual elements
- [ ] Handle forward/backward references
- [ ] Build reference graph
- [ ] Detect broken references

#### 4.4 Search Indexer
**File:** `inference/linking/search_indexer.py`

**Core Function:**
```python
def build_search_index(
    document_structure: Dict
) -> Dict:
    """
    Build multiple indices for fast querying.
    """
```

**Tasks:**
- [ ] Build type-based index
- [ ] Build page-based index
- [ ] Build keyword-based index (simple)
- [ ] Build spatial index (by region)
- [ ] Save indices

### Phase 5: Integration (Weeks 9-10)

#### 5.1 Update Core Functions

**Modify `inference/pdf.py`:**
```python
def process_pdf(
    pdf_path: str,
    output_dir: Optional[str] = None,
    extract_elements: bool = True,        # NEW
    generate_json: bool = True,           # NEW
    build_manifest: bool = True,          # NEW
    extraction_options: Optional[Dict] = None  # NEW
) -> Dict:                                # Changed return type
    """
    Enhanced PDF processing with structured output.
    
    Returns:
        {
            "markdown": str,              # Original markdown text
            "structure": dict,            # NEW: Full JSON structure
            "manifest": dict,             # NEW: Image manifest
            "output_dir": str,            # Output location
            "stats": dict                 # Processing statistics
        }
    """
```

**Modify `inference/image.py`:**
```python
def process_image(
    image_path: str,
    output_dir: Optional[str] = None,
    extract_elements: bool = False,       # NEW
    generate_json: bool = False           # NEW
) -> Union[str, Dict]:                    # Enhanced return
    """
    Enhanced image processing with optional structured output.
    """
```

**Tasks:**
- [ ] Update function signatures (backward compatible)
- [ ] Add new parameters with sensible defaults
- [ ] Integrate extraction modules
- [ ] Update return types
- [ ] Maintain backward compatibility
- [ ] Update error handling

#### 5.2 Configuration System

**File:** `inference/config.py` (NEW)

```python
@dataclass
class ExtractionConfig:
    """Configuration for element extraction."""
    extract_elements: bool = True
    element_padding: int = 5
    min_element_size: int = 10
    image_format: str = 'jpg'
    image_quality: int = 95
    generate_overlays: bool = True

@dataclass
class StructuringConfig:
    """Configuration for JSON structuring."""
    generate_json: bool = True
    schema_version: str = 'v1'
    include_statistics: bool = True
    include_hierarchy: bool = True
    validate_schema: bool = True

@dataclass
class LinkingConfig:
    """Configuration for linking system."""
    build_manifest: bool = True
    extract_context: bool = True
    resolve_references: bool = True
    build_search_index: bool = True
    context_window: int = 2

@dataclass
class ProcessingConfig:
    """Complete processing configuration."""
    extraction: ExtractionConfig = field(default_factory=ExtractionConfig)
    structuring: StructuringConfig = field(default_factory=StructuringConfig)
    linking: LinkingConfig = field(default_factory=LinkingConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'ProcessingConfig':
        """Load from dictionary or JSON file."""
```

**Tasks:**
- [ ] Implement configuration dataclasses
- [ ] Add validation
- [ ] Support loading from JSON/YAML
- [ ] Add presets (minimal, standard, full)
- [ ] Document all options

#### 5.3 Enhanced Demo Scripts

**File:** `pdf_demo_enhanced.py` (NEW)

```python
"""Demo script showcasing enhanced PDF extraction."""

from pathlib import Path
from inference import process_pdf
from inference.config import ProcessingConfig
import json

def main() -> None:
    pdf_path = Path("test_files/pdf/2510.17820v1.pdf")
    output_dir = Path("test_files/pdf/enhanced_output")
    
    # Configure enhanced processing
    config = ProcessingConfig(
        extraction=ExtractionConfig(
            extract_elements=True,
            generate_overlays=True
        ),
        structuring=StructuringConfig(
            generate_json=True,
            include_hierarchy=True
        ),
        linking=LinkingConfig(
            build_manifest=True,
            resolve_references=True
        )
    )
    
    print(f"Processing {pdf_path.name} with enhanced extraction...")
    result = process_pdf(
        str(pdf_path),
        output_dir=str(output_dir),
        config=config
    )
    
    # Display results
    print(f"\n{'='*60}")
    print(f"Processing Complete!")
    print(f"{'='*60}")
    print(f"Output directory: {result['output_dir']}")
    print(f"\nStatistics:")
    print(f"  Total pages: {result['stats']['total_pages']}")
    print(f"  Total elements: {result['stats']['total_elements']}")
    print(f"  Element breakdown:")
    for elem_type, count in result['stats']['element_distribution'].items():
        print(f"    {elem_type}: {count}")
    
    print(f"\nGenerated files:")
    print(f"  - Combined markdown: {result['output_dir']}/document.md")
    print(f"  - Structure JSON: {result['output_dir']}/structure.json")
    print(f"  - Image manifest: {result['output_dir']}/image_manifest.json")
    print(f"  - Element images: {result['output_dir']}/page_*/elements/")
    print(f"  - Type overlays: {result['output_dir']}/page_*/overlays/")
    
    # Save pretty-printed structure
    structure_path = Path(result['output_dir']) / "structure_pretty.json"
    with open(structure_path, 'w') as f:
        json.dump(result['structure'], f, indent=2, ensure_ascii=False)
    print(f"\nPretty-printed structure saved to: {structure_path}")

if __name__ == "__main__":
    main()
```

**Tasks:**
- [ ] Create enhanced demo script
- [ ] Add visualization utilities
- [ ] Show before/after comparison
- [ ] Demonstrate querying capabilities
- [ ] Add performance benchmarks

### Phase 6: Testing & Documentation (Weeks 11-12)

#### 6.1 Comprehensive Testing

**Test Suite Structure:**
```
tests/
├── __init__.py
├── test_extraction/
│   ├── test_element_extractor.py
│   ├── test_bbox_processor.py
│   ├── test_image_cropper.py
│   └── test_overlay_generator.py
├── test_structuring/
│   ├── test_json_builder.py
│   ├── test_element_classifier.py
│   └── test_hierarchy_analyzer.py
├── test_linking/
│   ├── test_manifest_builder.py
│   ├── test_context_extractor.py
│   └── test_reference_resolver.py
├── test_integration/
│   ├── test_pdf_processing.py
│   ├── test_image_processing.py
│   └── test_config.py
├── test_data/
│   ├── simple_page.png
│   ├── complex_page.png
│   ├── multi_column.pdf
│   └── ground_truth.json
└── utils/
    ├── fixtures.py
    └── validators.py
```

**Testing Tasks:**
- [ ] Unit tests for all new modules (>80% coverage)
- [ ] Integration tests for full pipeline
- [ ] Test with diverse document types
- [ ] Edge case testing (empty pages, single elements, huge pages)
- [ ] Performance testing (memory, speed)
- [ ] Regression testing (ensure backward compatibility)

#### 6.2 Documentation

**Documentation Tasks:**
- [ ] Update `docs/PDF_PROCESSING_GUIDE.md` with new features
- [ ] Create `docs/STRUCTURED_EXTRACTION_GUIDE.md`
- [ ] Create `docs/API_REFERENCE.md` for new modules
- [ ] Add JSON schema documentation
- [ ] Create tutorial notebooks/examples
- [ ] Update README.md with new features
- [ ] Add inline code documentation (docstrings)
- [ ] Create migration guide for existing users

**Key Documentation Files:**
```
docs/
├── PDF_PROCESSING_GUIDE.md (UPDATE)
├── STRUCTURED_EXTRACTION_GUIDE.md (NEW)
├── API_REFERENCE.md (NEW)
├── MIGRATION_GUIDE.md (NEW)
├── schemas/
│   ├── document_structure.md
│   ├── element_metadata.md
│   └── image_manifest.md
├── examples/
│   ├── basic_structured_extraction.py
│   ├── custom_element_extraction.py
│   ├── querying_document_structure.py
│   └── building_search_index.py
└── reference/
    └── model_output_specification.md
```

---

## Expected Output Examples

### Example 1: Research Paper (16 pages)

**Before (Current):**
```
2510.17820v1_outputs/
├── 2510.17820v1.md              # 1 file: combined markdown
├── pages/                        # 16 files: page images
├── page_0001/
│   ├── result.mmd               # per-page markdown
│   ├── result_with_boxes.jpg    # annotated image
│   └── images/                  # only extracted figures
│       └── 0.jpg
└── ... (15 more pages)
```

**After (Enhanced):**
```
2510.17820v1_outputs/
├── 2510.17820v1.md              # Combined markdown (unchanged)
├── structure.json               # NEW: Full document structure
├── structure_pretty.json        # NEW: Human-readable JSON
├── image_manifest.json          # NEW: Image catalog with links
├── search_index.json            # NEW: Fast lookup indices
├── document_graph.json          # NEW: Element relationships
├── pages/                        # Page images (unchanged)
├── page_0001/
│   ├── result.mmd               # Per-page markdown (unchanged)
│   ├── result_with_boxes.jpg    # All boxes (unchanged)
│   ├── elements/                # NEW: Individual element images
│   │   ├── elem_0_title.jpg
│   │   ├── elem_0_title.json
│   │   ├── elem_1_paragraph.jpg
│   │   ├── elem_1_paragraph.json
│   │   ├── elem_2_image.jpg
│   │   ├── elem_2_image.json
│   │   ├── elem_3_paragraph.jpg
│   │   ├── elem_3_paragraph.json
│   │   └── ... (all elements)
│   ├── overlays/                # NEW: Type-specific overlays
│   │   ├── titles_only.jpg
│   │   ├── paragraphs_only.jpg
│   │   ├── images_only.jpg
│   │   └── all_types_colored.jpg
│   └── images/                  # Extracted figures (unchanged)
│       └── 0.jpg
├── page_0002/
│   └── ... (same structure)
└── ... (15 more pages)
```

### Example 2: Query Capabilities

**Before:**
```python
# Limited querying - must parse markdown
result = process_pdf("paper.pdf")
# Can only access raw markdown text
```

**After:**
```python
# Rich querying capabilities
result = process_pdf("paper.pdf")

# Get all images
images = [e for e in result['structure']['elements'] 
          if e['type'] == 'image']

# Find images on page 3
page3_images = [e for e in result['structure']['pages'][2]['elements']
                if e['type'] == 'image']

# Get context for an image
img = images[0]
context = img['relationships']['context']

# Find all tables
tables = result['manifest']['search_index']['by_type']['table']

# Get element by ID
elem = next(e for e in result['structure']['elements']
            if e['id'] == 'page_1_elem_2')

# Find references to "Figure 1"
refs = result['manifest']['references']['Figure 1']
```

---

## Success Criteria

### Functional Requirements
- [ ] Extract all element types (not just images)
- [ ] Generate valid JSON conforming to schema
- [ ] Create individual images for all bounding boxes
- [ ] Build accurate element relationships
- [ ] Link images to document context
- [ ] Support batch processing
- [ ] Maintain backward compatibility

### Quality Requirements
- [ ] >95% extraction accuracy (compared to manual inspection)
- [ ] <5% invalid bounding boxes
- [ ] JSON validates against schema
- [ ] All images have metadata
- [ ] All links are valid (no broken references)

### Performance Requirements
- [ ] <10% overhead compared to current processing
- [ ] Process 16-page paper in <20 minutes (current: ~15 min)
- [ ] Memory usage <8GB per page
- [ ] JSON file size <1MB per page

### Usability Requirements
- [ ] Clear API with sensible defaults
- [ ] Comprehensive documentation
- [ ] Example code for common use cases
- [ ] Easy migration path from current version
- [ ] Helpful error messages

---

## Risk Assessment & Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Model output format changes | High | Low | Version detection, fallback parsing |
| Unknown label types | Medium | Medium | Extensible type system, "unknown" type |
| Memory exhaustion on large pages | High | Medium | Streaming processing, pagination |
| Invalid coordinates | Medium | High | Validation, bounds checking, error recovery |
| JSON schema evolution | Medium | Low | Schema versioning, migration tools |

### Project Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Scope creep | High | Medium | Strict phase boundaries, MVP first |
| Testing complexity | Medium | High | Automated test suite, CI/CD |
| Documentation lag | Medium | Medium | Document-as-you-go, templates |
| User adoption | Medium | Low | Backward compatibility, gradual rollout |
| Performance regression | High | Low | Benchmarking, profiling, optimization |

---

## Dependencies

### External Libraries
- ✅ PyMuPDF (fitz) - Already used
- ✅ PIL/Pillow - Already used
- ✅ NumPy - Already used
- 🆕 jsonschema - For JSON validation
- 🆕 pydantic (optional) - For data validation

### Internal Dependencies
- Model output format stability
- Existing extraction pipeline
- File system structure
- Configuration system

---

## Timeline

### Phase 1: Foundation (Weeks 1-2)
- Week 1: Model output analysis, label type catalog
- Week 2: JSON schema design, module structure

### Phase 2: Core Extraction (Weeks 3-4)
- Week 3: Element extractor, bbox processor
- Week 4: Image cropper, overlay generator

### Phase 3: Structured Output (Weeks 5-6)
- Week 5: JSON builder, element classifier
- Week 6: Hierarchy analyzer, testing

### Phase 4: Linking System (Weeks 7-8)
- Week 7: Manifest builder, context extractor
- Week 8: Reference resolver, search indexer

### Phase 5: Integration (Weeks 9-10)
- Week 9: Core function updates, config system
- Week 10: Enhanced demo scripts, integration testing

### Phase 6: Testing & Documentation (Weeks 11-12)
- Week 11: Comprehensive testing, bug fixes
- Week 12: Documentation, examples, release prep

**Total Duration:** 12 weeks (~3 months)

---

## Future Enhancements (Post-v1.0)

### Short-term (3-6 months)
- [ ] Web UI for visualization and querying
- [ ] Export to structured formats (JSON-LD, XML, HTML)
- [ ] Advanced search (semantic search, fuzzy matching)
- [ ] Element comparison across versions
- [ ] Batch processing improvements

### Medium-term (6-12 months)
- [ ] Machine learning for element classification
- [ ] Automatic caption detection
- [ ] Table structure parsing (cell-level)
- [ ] Equation recognition improvements
- [ ] Multi-document analysis

### Long-term (12+ months)
- [ ] Real-time processing pipeline
- [ ] Distributed processing support
- [ ] Cloud integration
- [ ] API server mode
- [ ] Plugin architecture

---

## Resources & References

### Internal Documentation
- [PDF Processing Guide](../PDF_PROCESSING_GUIDE.md)
- [README.md](../../README.md)
- Model patch code: `model_patch/modeling_deepseekocr.py`

### External References
- JSON Schema specification: https://json-schema.org/
- Document AI best practices
- OCR evaluation metrics
- Information extraction techniques

### Tools & Libraries
- jsonschema: https://python-jsonschema.readthedocs.io/
- pydantic: https://docs.pydantic.dev/
- PIL/Pillow: https://pillow.readthedocs.io/
- PyMuPDF: https://pymupdf.readthedocs.io/

---

## Approval & Sign-off

**Plan Status:** Draft  
**Created:** October 22, 2025  
**Author:** Development Team  
**Reviewers:** TBD  

**Next Steps:**
1. Review and feedback on plan
2. Prioritization of features
3. Resource allocation
4. Phase 1 kickoff

---

## Appendix

### A. Coordinate System Reference

**Model Output Format:**
- Normalized coordinates: 0-999 range (not 0-1)
- Format: `[[x1, y1, x2, y2], ...]`
- Multiple boxes per element possible
- Origin: Top-left corner

**Conversion:**
```python
# Model output (0-999) → Absolute pixels
x1_abs = int(x1_norm / 999 * image_width)
y1_abs = int(y1_norm / 999 * image_height)

# Absolute pixels → Normalized (0-1)
x1_norm_01 = x1_abs / image_width
y1_norm_01 = y1_abs / image_height
```

### B. Label Type Reference (Preliminary)

| Label Type | Description | Current Extraction | Proposed Extraction |
|-----------|-------------|-------------------|-------------------|
| `image` | Figures, diagrams, photos | ✅ Yes | ✅ Enhanced |
| `paragraph` | Text paragraphs | ❌ No | ✅ Yes |
| `title` | Headings, titles | ❌ No | ✅ Yes |
| `table` | Tables | ❌ No | ✅ Yes |
| `equation` | Mathematical equations | ❌ No | ✅ Yes |
| `caption` | Image/table captions | ❌ No | ✅ Yes |
| `header` | Page headers | ❌ No | ✅ Yes |
| `footer` | Page footers | ❌ No | ✅ Yes |
| `list` | Bulleted/numbered lists | ❌ No | ✅ Yes |

*(Note: Actual label types to be confirmed in Phase 1)*

### C. File Size Estimates

**Current Output (16-page paper):**
- Markdown files: ~200 KB
- Page images (PNG, 200 DPI): ~45 MB
- Annotated images (JPG): ~25 MB
- Extracted figures: ~5 MB
- **Total: ~75 MB**

**Enhanced Output (16-page paper, ~15 elements/page):**
- Markdown files: ~200 KB (same)
- Page images: ~45 MB (same)
- Annotated images: ~25 MB (same)
- Extracted figures: ~5 MB (same)
- Element images (240 total): ~50 MB
- Element metadata JSON (240 files): ~2 MB
- Type overlays (80 files): ~15 MB
- Structure JSON: ~500 KB
- Manifest JSON: ~200 KB
- **Total: ~143 MB (~2x increase)**

**Storage Optimization Options:**
- Use JPEG for element images (already planned)
- Compress JSON (gzip)
- Skip overlay generation (optional)
- Use lower quality for element thumbnails

---

*End of Plan*
