#!/usr/bin/env python3
"""
Quick test of enhanced image processing on a single page.
"""

from pathlib import Path
from inference import process_image_enhanced
import json


def main():
    print("="*70)
    print("Enhanced Image Processing Test")
    print("="*70)
    
    # Use existing page image
    page_image = Path("test_files/pdf/2510.17820v1_outputs/pages/page_0001.png")
    
    if not page_image.exists():
        print(f"\nTest image not found: {page_image}")
        print("Please run pdf_demo.py first to generate test data.")
        return 1
    
    print(f"\nProcessing: {page_image}")
    
    # Create output directory
    output_dir = Path("test_files/test_enhanced_page")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Output: {output_dir}")
    
    try:
        print("\nRunning enhanced processing...")
        result = process_image_enhanced(
            image_path=str(page_image),
            output_dir=str(output_dir),
            generate_overlays=True,
            save_elements=True,
        )
        
        print("\n✓ Processing complete!")
        
        # Print summary
        print(f"\nExtracted {len(result['elements'])} elements:")
        
        from collections import Counter
        type_counts = Counter(e['type'] for e in result['elements'])
        for element_type, count in type_counts.most_common():
            print(f"  {element_type:20s}: {count:4d}")
        
        print(f"\nSaved {len(result['element_paths'])} element images")
        print(f"Generated {len(result['overlay_paths'])} overlay images")
        
        # Show first few elements
        print("\nFirst 3 elements:")
        for elem in result['elements'][:3]:
            print(f"\n  {elem['id']}")
            print(f"    Type: {elem['type']}")
            print(f"    Bounding boxes: {elem['metrics']['num_boxes']}")
            print(f"    Size: {elem['metrics']['width']:.0f} x {elem['metrics']['height']:.0f}")
        
        print(f"\n✓ Test completed successfully!")
        print(f"\nCheck outputs in: {output_dir}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
