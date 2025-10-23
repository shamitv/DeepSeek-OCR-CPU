"""
Script to analyze model output and catalog label types.
This helps understand what types of elements the model detects.
"""

import re
from pathlib import Path
from collections import Counter
import json


def extract_grounding_references(text):
    """Extract all grounding references from model output."""
    pattern = r'<\|ref\|>(.*?)<\|/ref\|><\|det\|>(.*?)<\|/det\|>'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches


def analyze_label_types(matches):
    """Analyze and count label types."""
    label_types = Counter()
    coordinate_formats = []
    
    for label_type, coords in matches:
        label_types[label_type] += 1
        
        # Store a few examples of coordinate formats
        if len(coordinate_formats) < 10:
            try:
                coords_parsed = eval(coords)
                coordinate_formats.append({
                    'label_type': label_type,
                    'coords': coords_parsed,
                    'num_boxes': len(coords_parsed) if isinstance(coords_parsed, list) else 1
                })
            except:
                pass
    
    return label_types, coordinate_formats


def process_test_file(file_path):
    """Process a test file and extract information."""
    print(f"\n{'='*70}")
    print(f"Analyzing: {file_path}")
    print(f"{'='*70}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract grounding references
    matches = extract_grounding_references(content)
    
    if not matches:
        print("No grounding references found in this file.")
        return None
    
    print(f"\nTotal grounding references found: {len(matches)}")
    
    # Analyze label types
    label_types, coord_examples = analyze_label_types(matches)
    
    print(f"\nLabel types detected:")
    for label_type, count in label_types.most_common():
        print(f"  - {label_type:20s}: {count:4d} occurrences")
    
    print(f"\nCoordinate format examples:")
    for i, example in enumerate(coord_examples[:3], 1):
        print(f"\n  Example {i}:")
        print(f"    Label: {example['label_type']}")
        print(f"    Num boxes: {example['num_boxes']}")
        if example['coords']:
            first_box = example['coords'][0] if isinstance(example['coords'], list) else example['coords']
            print(f"    First box: {first_box}")
    
    return {
        'file': str(file_path),
        'total_refs': len(matches),
        'label_types': dict(label_types),
        'coordinate_examples': coord_examples
    }


def main():
    """Main analysis function."""
    print("\n" + "="*70)
    print("DeepSeek OCR Model Output Analysis")
    print("="*70)
    
    # Find test output files
    test_dir = Path("test_files/pdf/2510.17820v1_outputs")
    
    if not test_dir.exists():
        print(f"\nTest directory not found: {test_dir}")
        print("Please run pdf_demo.py first to generate test outputs.")
        return
    
    # Collect all results
    all_results = []
    
    # Process page markdown files (these should have grounding refs)
    page_dirs = sorted(test_dir.glob("page_*"))
    
    for page_dir in page_dirs[:3]:  # Analyze first 3 pages
        result_file = page_dir / "result.mmd"
        if result_file.exists():
            result = process_test_file(result_file)
            if result:
                all_results.append(result)
    
    # Save summary
    if all_results:
        summary_file = Path("docs/reference/model_output_analysis.json")
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n{'='*70}")
        print(f"Summary saved to: {summary_file}")
        print(f"{'='*70}\n")
    else:
        print("\nNo grounding references found in any files.")
        print("The model output may have been post-processed to remove grounding tags.")


if __name__ == "__main__":
    main()
