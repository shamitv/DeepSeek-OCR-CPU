"""PDF inference utilities for DeepSeek OCR on CPU."""

from pathlib import Path
from typing import Optional

from .model_loader import load_model_and_tokenizer


def process_pdf(pdf_path: str, output_dir: Optional[str] = None) -> str:
    """Run OCR on each page of a PDF using the DeepSeek model on CPU."""
    pdf_path = Path(pdf_path).expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    output_dir_path = Path(output_dir).expanduser().resolve() if output_dir else None
    if output_dir_path:
        output_dir_path.mkdir(parents=True, exist_ok=True)

    tokenizer, model = load_model_and_tokenizer()

    prompt = "<image>\n<|grounding|>Convert the document to markdown. "
    result = model.infer_pdf(
        tokenizer,
        prompt=prompt,
        pdf_file=str(pdf_path),
        output_path=str(output_dir_path) if output_dir_path else "",
        save_results=bool(output_dir_path),
    )
    return result
