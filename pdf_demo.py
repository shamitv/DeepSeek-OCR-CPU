"""Demo script to run CPU inference on a sample PDF in test_files/pdf."""

from pathlib import Path

from inference import process_pdf


def main() -> None:
    pdfs_dir = Path("test_files/pdf").expanduser().resolve()
    if not pdfs_dir.is_dir():
        raise FileNotFoundError(f"PDF directory not found: {pdfs_dir}")

    pdf_files = [path for path in sorted(pdfs_dir.iterdir()) if path.suffix.lower() == ".pdf"]
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {pdfs_dir}")

    pdf_path = pdf_files[0]
    output_dir = pdfs_dir / f"{pdf_path.stem}_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing {pdf_path.name}...")
    result = process_pdf(str(pdf_path), output_dir=str(output_dir))
    print(f"Result for {pdf_path.name}: {result}")


if __name__ == "__main__":
    main()
