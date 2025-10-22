"""Image inference utilities for DeepSeek OCR on CPU."""

from pathlib import Path
from typing import Optional, Dict, Union
from PIL import Image

from .model_loader import load_model_and_tokenizer


def process_image(image_path: str, output_dir: Optional[str] = None) -> str:
    """Run OCR on a single image using the DeepSeek model on CPU."""
    image_path = str(Path(image_path).expanduser().resolve())
    output_dir_path: Optional[Path] = None
    if output_dir is not None:
        output_dir_path = Path(output_dir).expanduser().resolve()
        output_dir = str(output_dir_path)

    tokenizer, model = load_model_and_tokenizer()

    prompt = "<image>\n<|grounding|>Convert the document to markdown. "
    result = model.infer(
        tokenizer,
        prompt=prompt,
        image_file=image_path,
        output_path=output_dir or "",
        base_size=1024,
        image_size=640,
        crop_mode=True,
        save_results=bool(output_dir),
        test_compress=True,
    )
    if result is None and output_dir_path:
        result_file = output_dir_path / "result.mmd"
        if result_file.is_file():
            result = result_file.read_text(encoding="utf-8")

    if result is None:
        raise RuntimeError("Model inference did not return any output.")

    return result


def process_image_enhanced(
    image_path: str,
    output_dir: Optional[str] = None,
    extract_options: Optional[Dict] = None,
    generate_overlays: bool = True,
    save_elements: bool = True,
) -> Dict:
    """
    Run OCR on a single image with enhanced element extraction.
    
    This function extends process_image to extract individual elements,
    generate type-specific overlays, and create structured output.
    
    Args:
        image_path: Path to input image
        output_dir: Directory for output files (required for enhanced mode)
        extract_options: Options for element extraction (see extract_all_elements)
        generate_overlays: Whether to generate type-specific overlay images
        save_elements: Whether to save individual element images
    
    Returns:
        Dictionary with:
            - 'markdown': Extracted markdown text
            - 'elements': List of extracted elements with metadata
            - 'element_paths': Dict mapping element IDs to saved image paths
            - 'overlay_paths': Dict mapping overlay types to image paths
            - 'raw_output': Raw model output with grounding references
    """
    if output_dir is None:
        raise ValueError("output_dir is required for enhanced processing")
    
    # Import extraction modules
    from .extraction import (
        extract_all_elements,
        save_all_elements,
        generate_type_overlays,
    )
    
    # Process with standard pipeline first
    markdown = process_image(image_path, output_dir)
    
    output_dir_path = Path(output_dir).expanduser().resolve()
    
    # Load the raw output with grounding references
    raw_output_path = output_dir_path / "result_raw.txt"
    if not raw_output_path.exists():
        raise RuntimeError(
            "Raw output file not found. Ensure the model is saving result_raw.txt"
        )
    
    with open(raw_output_path, 'r', encoding='utf-8') as f:
        raw_output = f.read()
    
    # Load the image
    image = Image.open(image_path)
    
    # Extract elements
    elements = extract_all_elements(
        image=image,
        model_output=raw_output,
        page_number=1,
        extract_options=extract_options,
    )
    
    result = {
        'markdown': markdown,
        'elements': elements,
        'raw_output': raw_output,
        'element_paths': {},
        'overlay_paths': {},
    }
    
    # Save individual elements
    if save_elements:
        elements_dir = output_dir_path / "elements"
        element_paths = save_all_elements(image, elements, elements_dir)
        result['element_paths'] = element_paths
    
    # Generate type-specific overlays
    if generate_overlays:
        overlays_dir = output_dir_path / "overlays"
        overlay_paths = generate_type_overlays(image, elements, overlays_dir)
        result['overlay_paths'] = overlay_paths
    
    return result
