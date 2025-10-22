#!/usr/bin/env bash

set -euo pipefail

VENV_DIR="${1:-.venv}"

if [ -d "${VENV_DIR}" ]; then
  echo "Virtual environment directory '${VENV_DIR}' already exists." >&2
  echo "Remove it or choose a different path before rerunning this script." >&2
  exit 1
fi

python3 -m venv "${VENV_DIR}"

source "${VENV_DIR}/bin/activate"

pip install --upgrade pip

pip install --index-url https://download.pytorch.org/whl/cpu torch==2.6.0+cpu torchvision==0.21.0+cpu
pip install huggingface-hub

echo "Virtual environment created at '${VENV_DIR}' with CPU packages and huggingface-hub installed."
