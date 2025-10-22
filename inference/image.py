"""Image inference utilities for DeepSeek OCR on CPU."""

from pathlib import Path
from typing import Optional

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
