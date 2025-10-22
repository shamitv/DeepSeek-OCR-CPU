"""PDF inference utilities for DeepSeek OCR on CPU."""

from pathlib import Path
from typing import List, Optional

from .image import process_image
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
