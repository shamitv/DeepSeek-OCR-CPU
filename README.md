# DeepSeek-OCR CPU Toolkit

This repository provides a CPU-first workflow for running DeepSeek OCR without CUDA or a discrete GPU. It includes setup automation, local model patching for CPU inference, and demo scripts for processing images and PDFs.

The original DeepSeek OCR documentation remains in `README-source.md` for reference to research notes, GPU instructions, and upstream visuals.

## Prerequisites
- Python 3.12 (tested)
- Sufficient disk space (~7 GB) to download the model checkpoint
- Optional: `git`, `venv`, and other standard build tools (already available on most Linux systems)

## One-time Setup
Run the provided script to create a fresh virtual environment, install CPU-only dependencies, download the DeepSeek OCR model, and apply the local CPU patches:

```bash
bash setup/setup_cpu_env.sh
```

The script creates a `.venv/` virtual environment in the repository root by default. You can supply a custom path as the first argument (e.g., `bash setup/setup_cpu_env.sh ~/.virtualenvs/dpsk-cpu`).

**What the setup does:**
- Creates and activates the specified Python virtual environment
- Installs `torch==2.6.0+cpu` and `torchvision==0.21.0+cpu` using the official CPU wheel index
- Installs all project requirements from `requirements.txt`
- Downloads the Hugging Face model `deepseek-ai/DeepSeek-OCR` into `model_data/deepseek-ai/DeepSeek-OCR`
- Copies any files from `model_patch/` into the downloaded model directory so the model runs entirely on CPU (removes all `.cuda()` calls, adjusts autocast, etc.)

You can re-run the setup script at any time to refresh the virtual environment or reapply patches after updating `model_patch/`.

## Running the Image Demo
Once the setup is complete, activate the virtual environment and run the demo script to OCR every supported image inside `test_files/images/`:

```bash
source .venv/bin/activate
python image_demo.py
```

The demo writes outputs (Markdown text plus any referenced images) into `test_files/images/outputs/` and prints the extracted content to the terminal.

## Running the PDF Demo
Activate the virtual environment and run the demo script to OCR the first PDF found in `test_files/pdf/`:

```bash
source .venv/bin/activate
python pdf_demo.py
```

The script creates an output folder named after the PDF stem (for example, `test_files/pdf/sample_outputs/`) and stores the extracted Markdown there while printing the results to the terminal.

## Running the PDF Utilities
Two helper functions live in the `inference/` package for custom workflows:

- `inference.pdf_to_images.pdf_to_images(...)`: converts a PDF into page images using PyMuPDF (configurable DPI and format).
- `inference.pdf.process_pdf(...)`: runs OCR over a PDF, leveraging the same CPU-only model pipeline as the image demo.

Import the functions after activating the virtual environment:

```python
from inference import process_image, process_pdf, pdf_to_images

# Single image
markdown_text = process_image("/path/to/image.png", output_dir="/tmp/results")

# Entire PDF (returns markdown per page)
markdown_pages = process_pdf("/path/to/document.pdf", output_dir="/tmp/pdf_results")

# Convert a PDF to images first
images = pdf_to_images("/path/to/document.pdf", "/tmp/pdf_images", dpi=200)
```

## Notes on Local Model Patching
- The downloaded model lives under `model_data/deepseek-ai/DeepSeek-OCR/` and is ignored by Git.
- Customizations for CPU inference reside in `model_patch/`. Update those files as needed and rerun the setup script to sync them into the active model.
- The inference helpers reuse the locally patched model by loading it with `local_files_only=True`, so no additional downloads occur during runtime.

## Regenerating the Environment
If you want a clean start, delete `.venv/` and `model_data/`, then rerun `setup/setup_cpu_env.sh`. This ensures the next run downloads the model afresh and reapplies patches cleanly.

## Next Steps
- Add CLI wrappers or REST bindings as needed for your deployment scenario
- Experiment with prompt customization within `image_demo.py` or `inference/`
- Extend the patch directory to support additional CPU tweaks or model variants
