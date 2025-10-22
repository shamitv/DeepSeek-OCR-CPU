"""Demo script to run CPU inference on all images in test_files/images."""

from pathlib import Path

from inference import process_image


def main() -> None:
    images_dir = Path("test_files/images").expanduser().resolve()
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {images_dir}")

    output_dir = images_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    for image_path in sorted(images_dir.glob("*")):
        if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}:
            continue
        print(f"Processing {image_path.name}...")
        result = process_image(str(image_path), output_dir=str(output_dir))
        print(f"Result for {image_path.name}: {result}\n")


if __name__ == "__main__":
    main()
