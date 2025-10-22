"""Shared utilities for loading DeepSeek OCR tokenizer and model on CPU."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import torch
from transformers import AutoModel, AutoTokenizer

MODEL_ID = "deepseek-ai/DeepSeek-OCR"
MODEL_PATH = Path(__file__).resolve().parent.parent / "model_data" / MODEL_ID

_MODEL = None
_TOKENIZER = None


def load_model_and_tokenizer(device: str | torch.device = "cpu") -> Tuple[AutoTokenizer, AutoModel]:
	"""Load and cache the DeepSeek OCR tokenizer and model on the requested device."""
	global _MODEL, _TOKENIZER

	if not MODEL_PATH.exists():
		raise FileNotFoundError(
			f"Local model path '{MODEL_PATH}' not found. Run setup_cpu_env.sh first."
		)

	if isinstance(device, str):
		device = torch.device(device)

	if _TOKENIZER is None:
		_TOKENIZER = AutoTokenizer.from_pretrained(
			str(MODEL_PATH),
			trust_remote_code=True,
			local_files_only=True,
		)

	if _MODEL is None:
		_MODEL = AutoModel.from_pretrained(
			str(MODEL_PATH),
			trust_remote_code=True,
			use_safetensors=True,
			local_files_only=True,
		).eval()

	if _MODEL.device != device:
		_MODEL.to(device)

	return _TOKENIZER, _MODEL
