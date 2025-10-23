"""PDF inference utilities for DeepSeek OCR on CPU."""

from pathlib import Path
from typing import List, Optional, Dict
import json

from .image import process_image, process_image_enhanced
from .pdf_to_images import pdf_to_images


def _convert_pdf_to_images(pdf_path: Path, output_dir: Path) -> List[str]:
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    return pdf_to_images(str(pdf_path), str(pages_dir))


def process_pdf(pdf_path: str, output_dir: Optional[str] = None) -> str:
    """Run OCR on each PDF page by converting to images and aggregating results."""
    pdf_path_obj = Path(pdf_path).expanduser().resolve()
    if not pdf_path_obj.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path_obj}")

    output_root = Path(output_dir).expanduser().resolve() if output_dir else pdf_path_obj.parent / f"{pdf_path_obj.stem}_outputs"
    output_root.mkdir(parents=True, exist_ok=True)

    image_paths = _convert_pdf_to_images(pdf_path_obj, output_root)
    if not image_paths:
        raise ValueError(f"No pages found in PDF: {pdf_path_obj}")

    page_markdowns: List[str] = []
    for index, image_path in enumerate(image_paths, start=1):
        page_output_dir = output_root / f"page_{index:04d}"
        page_output_dir.mkdir(parents=True, exist_ok=True)
        page_markdown = process_image(image_path, output_dir=str(page_output_dir))
        page_markdowns.append(page_markdown.strip())

    combined_markdown = "\n\n".join(
        f"<!-- Page {idx} -->\n{content}" if content else f"<!-- Page {idx} -->"
        for idx, content in enumerate(page_markdowns, start=1)
    )

    combined_path = output_root / f"{pdf_path_obj.stem}.md"
    combined_path.write_text(combined_markdown, encoding="utf-8")

    return combined_markdown


def process_pdf_enhanced(
    pdf_path: str,
    output_dir: Optional[str] = None,
    extract_options: Optional[Dict] = None,
    generate_overlays: bool = True,
    save_elements: bool = True,
) -> Dict:
    """
    Run OCR on each PDF page with enhanced element extraction.
    
    This extends process_pdf to extract individual elements, generate
    type-specific overlays, and create structured JSON output.
    
    Args:
        pdf_path: Path to input PDF
        output_dir: Directory for outputs (auto-generated if None)
        extract_options: Options for element extraction
        generate_overlays: Whether to generate type-specific overlay images
        save_elements: Whether to save individual element images
    
    Returns:
        Dictionary with:
            - 'markdown': Combined markdown text
            - 'pages': List of per-page results with elements
            - 'structure': Document structure JSON
            - 'output_dir': Path to output directory
    """
    pdf_path_obj = Path(pdf_path).expanduser().resolve()
    if not pdf_path_obj.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path_obj}")

    output_root = (
        Path(output_dir).expanduser().resolve() if output_dir 
        else pdf_path_obj.parent / f"{pdf_path_obj.stem}_outputs"
    )
    output_root.mkdir(parents=True, exist_ok=True)

    # Convert PDF to images
    image_paths = _convert_pdf_to_images(pdf_path_obj, output_root)
    if not image_paths:
        raise ValueError(f"No pages found in PDF: {pdf_path_obj}")

    # Process each page with enhanced extraction
    page_results = []
    page_markdowns = []
    
    for index, image_path in enumerate(image_paths, start=1):
        print(f"\nProcessing page {index}/{len(image_paths)}...")
        
        page_output_dir = output_root / f"page_{index:04d}"
        page_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced processing
        page_result = process_image_enhanced(
            image_path=image_path,
            output_dir=str(page_output_dir),
            extract_options=extract_options,
            generate_overlays=generate_overlays,
            save_elements=save_elements,
        )
        
        page_result['page_number'] = index
        page_result['image_path'] = image_path
        page_results.append(page_result)
        
        page_markdowns.append(page_result['markdown'].strip())

    # Create combined markdown
    combined_markdown = "\n\n".join(
        f"<!-- Page {idx} -->\n{content}" if content else f"<!-- Page {idx} -->"
        for idx, content in enumerate(page_markdowns, start=1)
    )

    combined_path = output_root / f"{pdf_path_obj.stem}.md"
    combined_path.write_text(combined_markdown, encoding="utf-8")

    # Build document structure
    all_elements = []
    for page_result in page_results:
        all_elements.extend(page_result['elements'])
    
    document_structure = {
        'document_metadata': {
            'source_file': str(pdf_path_obj),
            'filename': pdf_path_obj.name,
            'num_pages': len(page_results),
            'total_elements': len(all_elements),
        },
        'pages': [
            {
                'page': result['page_number'],
                'num_elements': len(result['elements']),
                'element_types': list(set(e['type'] for e in result['elements'])),
            }
            for result in page_results
        ],
    }
    
    # Save structure JSON
    structure_path = output_root / "document_structure.json"
    with open(structure_path, 'w', encoding='utf-8') as f:
        json.dump(document_structure, f, indent=2)
    
    # Save detailed elements per page
    for page_result in page_results:
        page_num = page_result['page_number']
        page_dir = output_root / f"page_{page_num:04d}"
        elements_json_path = page_dir / "elements.json"
        
        with open(elements_json_path, 'w', encoding='utf-8') as f:
            json.dump(page_result['elements'], f, indent=2)
    
    return {
        'markdown': combined_markdown,
        'pages': page_results,
        'structure': document_structure,
        'output_dir': str(output_root),
    }
