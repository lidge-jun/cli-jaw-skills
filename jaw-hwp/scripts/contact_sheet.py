#!/usr/bin/env python3
"""Generate a contact sheet (page grid) from a PDF for quick visual QA.

Renders all pages into a single grid image so you can review
an entire document at a glance instead of page-by-page.

Usage:
    python contact_sheet.py input.pdf -o overview.jpg
    python contact_sheet.py input.pdf --cols 3 --dpi 120 -o overview.jpg

Dependencies:
    - pdftoppm (poppler): brew install poppler / apt install poppler-utils
    - Pillow: pip install Pillow
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def contact_sheet(
    pdf_path: str,
    output_path: str,
    cols: int = 4,
    dpi: int = 100,
) -> int:
    """Render PDF pages into a single grid image.

    Returns the number of pages rendered.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["pdftoppm", "-jpeg", "-r", str(dpi), pdf_path, f"{tmpdir}/page"],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pdftoppm failed: {result.stderr.decode()}")

        pages = sorted(Path(tmpdir).glob("page-*.jpg"))
        if not pages:
            raise RuntimeError("No pages rendered from PDF")

        imgs = [Image.open(p) for p in pages]
        pw, ph = imgs[0].size
        rows = -(-len(imgs) // cols)  # ceil division
        sheet = Image.new("RGB", (pw * cols, ph * rows), "white")

        for i, img in enumerate(imgs):
            x = (i % cols) * pw
            y = (i // cols) * ph
            sheet.paste(img, (x, y))

        sheet.save(output_path, quality=85)
        return len(imgs)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a contact sheet (page grid) from a PDF"
    )
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output image path (e.g. overview.jpg)",
    )
    parser.add_argument("--cols", type=int, default=4, help="Columns in grid (default: 4)")
    parser.add_argument("--dpi", type=int, default=100, help="Render DPI (default: 100)")
    args = parser.parse_args()

    if not Path(args.input).is_file():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    n = contact_sheet(args.input, args.output, cols=args.cols, dpi=args.dpi)
    print(f"Contact sheet: {n} pages → {args.output} ({args.cols} cols, {args.dpi} dpi)")


if __name__ == "__main__":
    main()
