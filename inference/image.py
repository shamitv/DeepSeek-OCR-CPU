"""Image inference utilities for DeepSeek OCR on CPU."""

from pathlib import Path
from typing import Optional

from transformers import AutoModel, AutoTokenizer

MODEL_ID = "deepseek-ai/DeepSeek-OCR"


def process_image(image_path: str, output_dir: Optional[str] = None) -> str:
    """Run OCR on a single image using the DeepSeek model on CPU."""
    image_path = str(Path(image_path).expanduser().resolve())
    if output_dir is not None:
        output_dir = str(Path(output_dir).expanduser().resolve())

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        use_safetensors=True,
    )
    model = model.eval().to("cpu")

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
    return result
