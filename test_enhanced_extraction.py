"""
Test script for enhanced element extraction.

This demonstrates the new extraction capabilities on a sample page.
"""

from pathlib import Path
from PIL import Image
import json

# Import the new extraction modules
from inference.extraction import (
    extract_all_elements,
    save_all_elements,
    generate_type_overlays,
)


def test_extraction():
    """Test element extraction on a sample page."""
    
    # Use an existing test output
    test_page_dir = Path("test_files/pdf/2510.17820v1_outputs/page_0001")
    
    if not test_page_dir.exists():
        print("Test directory not found. Please run pdf_demo.py first.")
        return
    
    # Load the page image
    page_image_path = Path("test_files/pdf/2510.17820v1_outputs/pages/page_0001.png")
    if not page_image_path.exists():
        print(f"Page image not found: {page_image_path}")
        return
    
    print("Loading page image...")
    image = Image.open(page_image_path)
    print(f"Image size: {image.size}")
    
    # Read the result file - but it won't have grounding refs
    result_file = test_page_dir / "result.mmd"
    if not result_file.exists():
        print(f"Result file not found: {result_file}")
        return
    
    with open(result_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Content length: {len(content)} characters")
    
    # Check for grounding references
    if '<|ref|>' in content:
        print("\n✓ Grounding references found in output!")
        
        # Extract elements
        print("\nExtracting elements...")
        elements = extract_all_elements(image, content, page_number=1)
        
        print(f"Extracted {len(elements)} elements")
        
        # Print summary
        from collections import Counter
        type_counts = Counter(e['type'] for e in elements)
        print("\nElement types:")
        for element_type, count in type_counts.most_common():
            print(f"  - {element_type:20s}: {count:4d}")
        
        # Create output directory for enhanced extraction
        output_dir = test_page_dir / "enhanced_extraction"
        output_dir.mkdir(exist_ok=True)
        
        # Save individual elements
        print("\nSaving individual elements...")
        elements_dir = output_dir / "elements"
        saved_paths = save_all_elements(image, elements, elements_dir)
        print(f"Saved {len(saved_paths)} element images to {elements_dir}")
        
        # Generate type-specific overlays
        print("\nGenerating type-specific overlays...")
        overlays_dir = output_dir / "overlays"
        overlay_paths = generate_type_overlays(image, elements, overlays_dir)
        print(f"Generated {len(overlay_paths)} overlay images in {overlays_dir}")
        
        # Save elements as JSON
        elements_json_path = output_dir / "elements.json"
        with open(elements_json_path, 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2)
        print(f"\nSaved element metadata to {elements_json_path}")
        
        print("\n✓ Enhanced extraction test completed successfully!")
        
    else:
        print("\n✗ No grounding references found in output.")
        print("The model output has been post-processed to remove grounding tags.")
        print("\nTo test extraction, we need to modify the model to preserve raw output.")
        print("This requires updating modeling_deepseekocr.py to return the raw output")
        print("with grounding references before they are stripped.")


def main():
    print("="*70)
    print("Enhanced Element Extraction Test")
    print("="*70)
    
    test_extraction()


if __name__ == "__main__":
    main()
