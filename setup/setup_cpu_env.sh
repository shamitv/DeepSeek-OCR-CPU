#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="${SCRIPT_DIR}/../requirements.txt"

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

echo "Virtual environment created at '${VENV_DIR}' with CPU packages, huggingface-hub, and requirements installed."
