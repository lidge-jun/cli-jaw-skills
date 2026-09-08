#!/usr/bin/env python3
"""Column-based OCR: 이미지를 N열로 분할 → 각 열 OCR → 합치기.

Usage:
  python3 ocr_columns.py <image_path> [--cols N] [--header-rows PIXELS]

ASCII art 코드처럼 열 레이아웃 기반 이미지에 적합.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    sys.exit(1)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
OCR_SWIFT = os.path.join(SCRIPTS_DIR, "ocr.swift")


def crop_columns(img_path: str, n_cols: int, header_px: int = 0) -> list:
    """이미지를 header + N columns로 분할, 임시 파일로 저장."""
    img = Image.open(img_path)
    w, h = img.size
    crops = []
    tmpdir = tempfile.mkdtemp()

    # Header (상단 N픽셀)
    if header_px > 0:
        header = img.crop((0, 0, w, header_px))
        hdr_path = os.path.join(tmpdir, "col_00_header.png")
        header.save(hdr_path)
        crops.append(("header", hdr_path))

    # Columns (header 아래부터)
    body_top = header_px
    col_width = w // n_cols
    for i in range(n_cols):
        left = i * col_width
        right = (i + 1) * col_width if i < n_cols - 1 else w
        col = img.crop((left, body_top, right, h))
        col_path = os.path.join(tmpdir, f"col_{i+1:02d}.png")
        col.save(col_path)
        crops.append((f"col_{i+1}", col_path))

    return crops


def ocr_image(img_path: str) -> str:
    """Apple Vision OCR on a single image."""
    result = subprocess.run(
        ["swift", OCR_SWIFT, "1", img_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return f"[OCR ERROR: {result.stderr}]"
    try:
        data = json.loads(result.stdout)
        return data[0]["text"] if data else ""
    except (json.JSONDecodeError, IndexError, KeyError):
        return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description="Column-based OCR")
    parser.add_argument("image", help="Input image path")
    parser.add_argument("--cols", type=int, default=5, help="Number of columns (default: 5)")
    parser.add_argument("--header-px", type=int, default=0, help="Header height in pixels (default: 0)")
    parser.add_argument("--output", default="json", choices=["json", "text"], help="Output format")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"ERROR: {args.image} not found", file=sys.stderr)
        sys.exit(1)

    # 1. Crop
    crops = crop_columns(args.image, args.cols, args.header_px)
    print(f"Split into {len(crops)} parts", file=sys.stderr)

    # 2. OCR each part
    results = []
    for name, path in crops:
        text = ocr_image(path)
        results.append({"name": name, "text": text})
        print(f"  {name}: {len(text)} chars", file=sys.stderr)

    # 3. Output
    if args.output == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"=== {r['name']} ===")
            print(r["text"])
            print()


if __name__ == "__main__":
    main()
