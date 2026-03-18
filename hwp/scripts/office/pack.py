#!/usr/bin/env python3
"""Pack a directory back into an HWPX (ZIP) file.

The mimetype file is stored as the first entry with ZIP_STORED (no compression),
per OPC packaging conventions.

Before packing, XML files are processed:
  1. linesegarray elements are stripped (layout cache — Hancom recalculates on open)
  2. XML is minified to single-line (matching Hancom's native save format)

Usage:
    python pack.py input_dir/ output.hwpx
    python pack.py input_dir/ output.hwpx --keep-linesegarray
    python pack.py input_dir/ output.hwpx --no-minify
"""

import argparse
import os
import re
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile


def strip_linesegarray(xml_text: str) -> str:
    """Remove all linesegarray elements from XML text.

    linesegarray is a layout cache that stores line break positions,
    vertical offsets, and text heights. When text is modified but
    linesegarray is not removed, Hancom uses the stale cache, causing:
      - Text compressed/squeezed into fewer lines than needed
      - Line breaks not occurring where they should
      - Last line of a paragraph being visually crushed

    Hancom recalculates linesegarray automatically when the document
    is opened and the element is absent.

    Handles both namespaced (hp:linesegarray) and non-namespaced variants.
    """
    result = re.sub(
        r'<(?:hp:)?linesegarray[^>]*>.*?</(?:hp:)?linesegarray>',
        '',
        xml_text,
        flags=re.DOTALL,
    )
    # Also handle self-closing variant (unlikely but safe)
    result = re.sub(
        r'<(?:hp:)?linesegarray[^/]*/>', '', result
    )
    return result


def minify_xml(xml_text: str) -> str:
    """Minify XML to single-line format matching Hancom's native save format.

    Removes whitespace between tags while preserving:
      - XML declaration (<?xml ...?>)
      - Text content inside elements (whitespace within <hp:t>...</hp:t> is significant)
    """
    # Separate XML declaration
    decl = ''
    body = xml_text
    m = re.match(r'(<\?xml[^?]*\?>)\s*', xml_text)
    if m:
        decl = m.group(1)
        body = xml_text[m.end():]

    # Remove whitespace between tags only (not within text content)
    minified = re.sub(r'>\s+<', '><', body.strip())
    return decl + minified


def pack(
    input_dir: str,
    hwpx_path: str,
    strip_lsa: bool = True,
    minify: bool = True,
) -> None:
    """Create HWPX archive from a directory.

    Args:
        input_dir: Path to the unpacked HWPX directory.
        hwpx_path: Output .hwpx file path.
        strip_lsa: If True, remove linesegarray elements from XML files.
        minify: If True, minify XML to single-line format.
    """
    root = Path(input_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Directory not found: {input_dir}")

    mimetype_file = root / "mimetype"
    if not mimetype_file.is_file():
        raise FileNotFoundError(
            f"Missing required 'mimetype' file in {input_dir}"
        )

    all_files = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
    )

    lsa_stripped = 0

    with ZipFile(hwpx_path, "w", ZIP_DEFLATED) as zf:
        # mimetype MUST be the first entry, stored without compression
        zf.write(mimetype_file, "mimetype", compress_type=ZIP_STORED)

        for rel_path in all_files:
            if rel_path == "mimetype":
                continue  # Already written

            full_path = root / rel_path

            if rel_path.endswith(".xml"):
                content = full_path.read_text(encoding="utf-8")

                if strip_lsa:
                    before = content.count("linesegarray")
                    content = strip_linesegarray(content)
                    after = content.count("linesegarray")
                    lsa_stripped += (before - after) // 2  # open+close = 2

                if minify:
                    content = minify_xml(content)

                zf.writestr(
                    rel_path,
                    content.encode("utf-8"),
                    compress_type=ZIP_DEFLATED,
                )
            else:
                zf.write(full_path, rel_path, compress_type=ZIP_DEFLATED)

    count = len(all_files)
    print(f"Packed: {input_dir} -> {hwpx_path}")
    print(f"  Files: {count} entries (mimetype first, ZIP_STORED)")
    if strip_lsa and lsa_stripped > 0:
        print(f"  Stripped: {lsa_stripped} linesegarray elements")
    if minify:
        print(f"  XML: minified to single-line format")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pack a directory into an HWPX (ZIP) file"
    )
    parser.add_argument("input", help="Input directory path")
    parser.add_argument("output", help="Output .hwpx file path")
    parser.add_argument(
        "--keep-linesegarray",
        action="store_true",
        help="Do not strip linesegarray elements (default: strip them)",
    )
    parser.add_argument(
        "--no-minify",
        action="store_true",
        help="Do not minify XML (keep pretty-printed format)",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        print(f"Error: Directory not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    pack(
        args.input,
        args.output,
        strip_lsa=not args.keep_linesegarray,
        minify=not args.no_minify,
    )


if __name__ == "__main__":
    main()
