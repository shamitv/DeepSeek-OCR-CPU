#!/usr/bin/env python3
"""
Enhanced PDF processing demo.

This demonstrates the new enhanced extraction capabilities including:
- Individual element extraction
- Type-specific overlays
- Structured JSON output
"""

from pathlib import Path
from inference import process_pdf_enhanced
import json


def main():
    print("="*70)
    print("Enhanced PDF Processing Demo")
    print("="*70)
    
    # Find a test PDF
    test_pdf_dir = Path("test_files/pdf")
    pdf_files = list(test_pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("\nNo PDF files found in test_files/pdf/")
        print("Please add a PDF file to test.")
        return
    
    # Use the first PDF
    pdf_path = pdf_files[0]
    print(f"\nProcessing: {pdf_path.name}")
    print(f"Full path: {pdf_path}")
    
    # Set output directory
    output_dir = test_pdf_dir / f"{pdf_path.stem}_enhanced_outputs"
    
    print(f"\nOutput will be saved to: {output_dir}")
    print("\nStarting enhanced processing...")
    print("This will:")
    print("  1. Convert PDF pages to images")
    print("  2. Run OCR on each page")
    print("  3. Extract individual elements (titles, paragraphs, images, etc.)")
    print("  4. Save each element as a separate image")
    print("  5. Generate type-specific overlay images")
    print("  6. Create structured JSON output")
    print()
    
    # Process with enhanced extraction
    try:
        result = process_pdf_enhanced(
            pdf_path=str(pdf_path),
            output_dir=str(output_dir),
            generate_overlays=True,
            save_elements=True,
        )
        
        print("\n" + "="*70)
        print("Processing Complete!")
        print("="*70)
        
        # Print summary
        print(f"\nDocument: {result['structure']['document_metadata']['filename']}")
        print(f"Pages processed: {result['structure']['document_metadata']['num_pages']}")
        print(f"Total elements: {result['structure']['document_metadata']['total_elements']}")
        
        print("\nPer-page summary:")
        for page_info in result['structure']['pages']:
            print(f"  Page {page_info['page']:2d}: {page_info['num_elements']:3d} elements "
                  f"({', '.join(page_info['element_types'])})")
        
        print(f"\nOutput structure:")
        print(f"  {output_dir}/")
        print(f"    ├── {pdf_path.stem}.md           # Combined markdown")
        print(f"    ├── document_structure.json       # Document structure")
        print(f"    ├── pages/                        # Page images")
        print(f"    └── page_XXXX/                    # Per-page results")
        print(f"        ├── result.mmd                # Page markdown")
        print(f"        ├── result_raw.txt            # Raw output with grounding refs")
        print(f"        ├── result_with_boxes.jpg     # Annotated image")
        print(f"        ├── elements.json             # Element metadata")
        print(f"        ├── elements/                 # Individual element images")
        print(f"        │   ├── page_XXXX_elem_XXXX_TYPE.jpg")
        print(f"        │   └── page_XXXX_elem_XXXX_TYPE.json")
        print(f"        ├── overlays/                 # Type-specific overlays")
        print(f"        │   ├── title_only.jpg")
        print(f"        │   ├── paragraph_only.jpg")
        print(f"        │   ├── image_only.jpg")
        print(f"        │   └── all_types_colored.jpg")
        print(f"        └── images/                   # Extracted figures")
        
        # Show example queries
        print("\n" + "="*70)
        print("Example Queries")
        print("="*70)
        
        # Count elements by type
        from collections import Counter
        all_elements = []
        for page in result['pages']:
            all_elements.extend(page['elements'])
        
        type_counts = Counter(e['type'] for e in all_elements)
        
        print("\nElement types in document:")
        for element_type, count in type_counts.most_common():
            print(f"  {element_type:20s}: {count:4d}")
        
        # Find images
        images = [e for e in all_elements if e['type'] == 'image']
        print(f"\nFound {len(images)} images in document")
        if images:
            print("First image:")
            img = images[0]
            print(f"  ID: {img['id']}")
            print(f"  Page: {img['page']}")
            print(f"  Bounding boxes: {img['metrics']['num_boxes']}")
            print(f"  Size: {img['metrics']['width']:.0f} x {img['metrics']['height']:.0f} pixels")
        
        # Find titles
        titles = [e for e in all_elements if e['type'] == 'title']
        print(f"\nFound {len(titles)} titles in document")
        
        print("\n✓ Enhanced processing completed successfully!")
        print(f"\nExplore the outputs in: {output_dir}")
        
    except Exception as e:
        print(f"\n✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
