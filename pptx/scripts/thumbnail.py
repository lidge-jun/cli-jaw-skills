"""Generate thumbnail grids from PPTX slides.

Converts PPTX → PDF → PNG images, then arranges them in a contact-sheet grid.

Requirements:
    - LibreOffice (soffice)
    - Poppler (pdftoppm)
    - Pillow (PIL)

Usage:
    python thumbnail.py <input.pptx> <output.png>
    python thumbnail.py <input.pptx> <output.png> --cols 3 --dpi 150
    python thumbnail.py <input.pptx> <output_dir/> --individual  # one PNG per slide
"""

import argparse
import glob
import subprocess
import sys
import tempfile
from pathlib import Path

from ooxml.soffice import run_soffice

try:
    from PIL import Image
except ImportError:
    Image = None


def create_thumbnails(
    input_path: str,
    output_path: str,
    cols: int = 4,
    dpi: int = 150,
    individual: bool = False,
) -> str:
    """Generate slide thumbnails from a PPTX file."""
    if Image is None:
        return "Error: Pillow is required (pip install Pillow)"

    src = Path(input_path).resolve()
    dst = Path(output_path).resolve()

    if not src.exists():
        return f"Error: {input_path} does not exist"

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # Step 1: PPTX → PDF via LibreOffice
            pdf_result = run_soffice(
                [
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(tmp_path),
                    str(src),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            pdf_files = list(tmp_path.glob("*.pdf"))
            if not pdf_files:
                return f"Error: PDF conversion failed. soffice stderr: {pdf_result.stderr}"
            pdf_path = pdf_files[0]

            # Step 2: PDF → PNG images via pdftoppm
            img_prefix = str(tmp_path / "slide")
            pdftoppm_result = subprocess.run(
                ["pdftoppm", "-png", "-r", str(dpi), str(pdf_path), img_prefix],
                capture_output=True,
                text=True,
                timeout=120,
            )

            slide_images = sorted(glob.glob(f"{img_prefix}-*.png"))
            if not slide_images:
                # Try alternative naming (some pdftoppm versions use different patterns)
                slide_images = sorted(glob.glob(f"{img_prefix}*.png"))

            if not slide_images:
                return f"Error: pdftoppm produced no images. stderr: {pdftoppm_result.stderr}"

            # Step 3: Output
            if individual:
                # Save individual slide images
                dst.mkdir(parents=True, exist_ok=True)
                for i, img_path in enumerate(slide_images, 1):
                    dest = dst / f"slide-{i:02d}.png"
                    Image.open(img_path).save(str(dest))
                return f"Generated {len(slide_images)} individual slide thumbnails → {output_path}"
            else:
                # Create contact sheet grid
                return _create_grid(slide_images, str(dst), cols)

    except FileNotFoundError as e:
        if "pdftoppm" in str(e):
            return "Error: pdftoppm not found. Install Poppler (brew install poppler)"
        return f"Error: {e}"
    except Exception as e:
        return f"Error: {e}"


def _create_grid(image_paths: list[str], output_path: str, cols: int) -> str:
    """Arrange slide images in a grid layout."""
    images = [Image.open(p) for p in image_paths]
    n = len(images)

    if n == 0:
        return "Error: no slide images to arrange"

    # All slides should be same size; use first as reference
    thumb_w, thumb_h = images[0].size

    rows = (n + cols - 1) // cols
    padding = 10  # pixels between slides
    label_h = 30  # height for slide number label

    grid_w = cols * thumb_w + (cols + 1) * padding
    grid_h = rows * (thumb_h + label_h) + (rows + 1) * padding

    grid = Image.new("RGB", (grid_w, grid_h), "white")

    for i, img in enumerate(images):
        col = i % cols
        row = i // cols
        x = padding + col * (thumb_w + padding)
        y = padding + row * (thumb_h + label_h + padding)

        # Add border
        border_color = (200, 200, 200)
        bordered = Image.new("RGB", (thumb_w + 2, thumb_h + 2), border_color)
        bordered.paste(img, (1, 1))
        grid.paste(bordered, (x - 1, y - 1))

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    grid.save(output_path, quality=95)

    return f"Generated {cols}×{rows} thumbnail grid ({n} slides) → {output_path}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate slide thumbnail grids")
    parser.add_argument("input_file", help="Input PPTX file")
    parser.add_argument("output", help="Output PNG file or directory (with --individual)")
    parser.add_argument("--cols", type=int, default=4, help="Columns in grid (default: 4)")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for rendering (default: 150)")
    parser.add_argument("--individual", action="store_true", help="Save individual slide PNGs")
    args = parser.parse_args()

    msg = create_thumbnails(args.input_file, args.output, args.cols, args.dpi, args.individual)
    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
