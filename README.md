# DeepSeek-OCR CPU Docker

This repository packages DeepSeek OCR into a CPU-only Docker image so that you can run high quality OCR on everyday hardware. The image works without CUDA or a discrete GPU, and it has been tested on macOS and Windows hosts through Docker Desktop as well as on native Linux machines.

The upstream DeepSeek OCR project documentation now lives in `README-source.md`. Refer to that document whenever you need the original research notes, GPU setup guides, or visual assets from DeepSeek AI.

## How to use it
- Install Docker Desktop (macOS, Windows) or Docker Engine (Linux) so the `docker` command is available.
- Pull the published image: `docker pull <image-name-coming-soon>`.
- Run OCR on local files by mounting an input folder: `docker run --rm -v $PWD/data:/workspace/data <image-name-coming-soon> python run_cpu_ocr.py --input data/sample.png --out data/output`.
- Explore additional options via `docker run --rm <image-name-coming-soon> python run_cpu_ocr.py --help` once the CLI is finalized.

## How it works
Implementation details, benchmarking numbers, and architectural notes will be documented here as the CPU pipeline stabilizes.
