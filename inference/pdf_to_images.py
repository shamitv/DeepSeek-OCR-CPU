"""Utilities for exporting PDF pages to images for CPU inference."""

from pathlib import Path
from typing import List

import fitz  # PyMuPDF


def pdf_to_images(pdf_path: str, output_dir: str, dpi: int = 200, image_format: str = "png") -> List[str]:
    """Convert each page of a PDF to an image file and return the saved paths."""
    pdf_file = Path(pdf_path).expanduser().resolve()
    if not pdf_file.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_file}")

    output_root = Path(output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    if dpi <= 0:
        raise ValueError("dpi must be positive")
    if not image_format:
        raise ValueError("image_format must be non-empty")

    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)

    saved_paths: List[str] = []
    with fitz.open(pdf_file) as document:
        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            pix = page.get_pixmap(matrix=matrix)
            if pix.alpha:  # ensure consistent color space without alpha channel
                pix = fitz.Pixmap(pix, 0)
            image_name = f"page_{page_index + 1:04d}.{image_format.lower()}"
            image_path = output_root / image_name
            pix.save(image_path)
            saved_paths.append(str(image_path))

    return saved_paths
