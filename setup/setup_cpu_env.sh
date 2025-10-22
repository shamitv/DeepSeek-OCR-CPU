#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="${SCRIPT_DIR}/../requirements.txt"
MODEL_BASE_DIR="${SCRIPT_DIR}/../model_data"
MODEL_ID="deepseek-ai/DeepSeek-OCR"
MODEL_DIR="${MODEL_BASE_DIR}/${MODEL_ID}"
PATCH_DIR="${SCRIPT_DIR}/../model_patch"

VENV_DIR="${1:-.venv}"

if [ -d "${VENV_DIR}" ]; then
  echo "Virtual environment directory '${VENV_DIR}' already exists." >&2
  echo "Remove it or choose a different path before rerunning this script." >&2
  exit 1
fi

if [ ! -f "${REQ_FILE}" ]; then
  echo "Could not find requirements file at '${REQ_FILE}'." >&2
  exit 1
fi

python3 -m venv "${VENV_DIR}"

source "${VENV_DIR}/bin/activate"

pip install --upgrade pip

pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0+cpu torchvision==0.21.0+cpu
pip install huggingface-hub
pip install -r "${REQ_FILE}"

mkdir -p "${MODEL_BASE_DIR}"

if [ -d "${MODEL_DIR}" ] && [ "$(ls -A "${MODEL_DIR}" 2>/dev/null)" ]; then
  echo "Model directory '${MODEL_DIR}' already exists; skipping download."
else
  mkdir -p "${MODEL_DIR}"
  MODEL_DIR="${MODEL_DIR}" python - <<'PY'
import os
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="deepseek-ai/DeepSeek-OCR",
    local_dir=os.environ["MODEL_DIR"],
    local_dir_use_symlinks=False,
)
PY
  echo "Model 'deepseek-ai/DeepSeek-OCR' downloaded to '${MODEL_DIR}'."
fi

echo "Virtual environment created at '${VENV_DIR}' with dependencies installed and model data prepared."

if [ -d "${PATCH_DIR}" ] && [ "$(ls -A "${PATCH_DIR}" 2>/dev/null)" ]; then
  echo "Copying model patches from '${PATCH_DIR}' to '${MODEL_DIR}'."
  MODEL_DIR="${MODEL_DIR}" PATCH_DIR="${PATCH_DIR}" python - <<'PY'
import os
import shutil

patch_dir = os.environ["PATCH_DIR"]
model_dir = os.environ["MODEL_DIR"]

for root, dirs, files in os.walk(patch_dir):
    rel_root = os.path.relpath(root, patch_dir)
    dest_dir = model_dir if rel_root == "." else os.path.join(model_dir, rel_root)
    os.makedirs(dest_dir, exist_ok=True)
    for name in files:
        src_path = os.path.join(root, name)
        dest_path = os.path.join(dest_dir, name)
        shutil.copy2(src_path, dest_path)
PY
  echo "Model patches copied into '${MODEL_DIR}'."
else
  echo "Model patch directory '${PATCH_DIR}' not found or empty; skipping patch copy."
fi
