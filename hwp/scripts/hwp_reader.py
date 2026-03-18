#!/usr/bin/env python3
"""Read and extract content from HWP 5.0 binary files.

HWP 5.0 is an OLE Compound File containing streams like FileHeader,
DocInfo, and BodyText/Section0..N. Text is UTF-16LE encoded, and
body streams may be zlib-compressed.

This script extracts text and basic structure. For full editing,
upgrade to HWPX first (see SKILL.md Section 4).

Usage:
    python hwp_reader.py input.hwp                    # extract text
    python hwp_reader.py input.hwp --format json      # structured JSON
    python hwp_reader.py input.hwp --info              # file info only
    python hwp_reader.py input.hwp --list-streams      # list OLE streams

Dependencies:
    pip install olefile

For more complete parsing, use pyhwp's hwp5proc CLI:
    hwp5proc text input.hwp
    hwp5proc xml input.hwp
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

try:
    import olefile
except ImportError:
    print("Error: olefile is required. Install with: pip install olefile", file=sys.stderr)
    sys.exit(1)


def read_file_header(ole: olefile.OleFileIO) -> dict:
    """Read FileHeader stream to get version and flags."""
    data = ole.openstream("FileHeader").read()
    signature = data[:32].split(b"\x00")[0].decode("ascii", errors="replace")
    version_raw = struct.unpack_from("<I", data, 32)[0]
    flags = struct.unpack_from("<I", data, 36)[0]

    version = (
        f"{(version_raw >> 24) & 0xFF}."
        f"{(version_raw >> 16) & 0xFF}."
        f"{(version_raw >> 8) & 0xFF}."
        f"{version_raw & 0xFF}"
    )

    return {
        "signature": signature,
        "version": version,
        "compressed": bool(flags & 0x01),
        "encrypted": bool(flags & 0x02),
        "distribution": bool(flags & 0x04),
        "script": bool(flags & 0x08),
        "drm": bool(flags & 0x10),
        "xml_template": bool(flags & 0x20),
        "history": bool(flags & 0x40),
        "cert_signed": bool(flags & 0x80),
        "cert_encrypted": bool(flags & 0x100),
        "cert_drm": bool(flags & 0x200),
        "ccl": bool(flags & 0x400),
    }


def extract_text_from_body(data: bytes) -> str:
    """Extract readable text from a BodyText section stream.

    Parses the record chain (Tag-Level-Size) and extracts text from
    HWPTAG_PARA_TEXT records (tag ID 67). Text is UTF-16LE encoded.
    Control characters (0x0001-0x001F) represent special objects
    (tables, images, etc.) and are replaced with markers.
    """
    text_parts: list[str] = []
    offset = 0

    while offset < len(data) - 4:
        # Record header: 4 bytes
        # Bits 0-9: tag ID, 10-19: level, 20-31: size
        header = struct.unpack_from("<I", data, offset)[0]
        tag_id = header & 0x3FF
        size = (header >> 20) & 0xFFF
        offset += 4

        # Extended size
        if size == 0xFFF:
            if offset + 4 > len(data):
                break
            size = struct.unpack_from("<I", data, offset)[0]
            offset += 4

        if offset + size > len(data):
            break

        # HWPTAG_PARA_TEXT = 67
        if tag_id == 67 and size > 0:
            try:
                raw = data[offset : offset + size]
                decoded = raw.decode("utf-16-le", errors="replace")
                # Replace control characters with readable markers
                clean = []
                for ch in decoded:
                    code = ord(ch)
                    if code == 0x0D or code == 0x0A:
                        clean.append("\n")
                    elif 0x0001 <= code <= 0x001F:
                        pass  # Skip control chars (table/image markers)
                    else:
                        clean.append(ch)
                text_parts.append("".join(clean))
            except Exception:
                pass

        offset += size

    return "\n".join(text_parts)


def read_hwp(path: str) -> dict:
    """Read an HWP 5.0 file and return structured content."""
    ole = olefile.OleFileIO(path)

    header = read_file_header(ole)

    if header["encrypted"]:
        ole.close()
        raise ValueError("Encrypted HWP files are not supported. Decrypt first.")

    # List all streams
    streams = ["/".join(entry) for entry in ole.listdir()]

    # Extract text from BodyText sections
    sections: list[str] = []
    section_streams = sorted(
        s for s in streams if s.startswith("BodyText/Section")
    )

    for stream_path in section_streams:
        raw = ole.openstream(stream_path).read()
        if header["compressed"]:
            try:
                raw = zlib.decompress(raw, -15)
            except zlib.error:
                try:
                    raw = zlib.decompress(raw)
                except zlib.error:
                    continue  # Skip if decompression fails

        text = extract_text_from_body(raw)
        if text.strip():
            sections.append(text)

    # Preview text (if available)
    preview = ""
    if "PrvText" in streams:
        try:
            preview = ole.openstream("PrvText").read().decode("utf-16-le", errors="replace")
        except Exception:
            pass

    ole.close()

    return {
        "file": str(path),
        "header": header,
        "streams": streams,
        "section_count": len(section_streams),
        "sections": sections,
        "preview": preview.strip(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read and extract content from HWP 5.0 binary files"
    )
    parser.add_argument("input", help="Input .hwp file path")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show file info only (no text extraction)",
    )
    parser.add_argument(
        "--list-streams",
        action="store_true",
        help="List all OLE streams in the file",
    )
    args = parser.parse_args()

    path = Path(args.input)
    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    result = read_hwp(str(path))

    if args.list_streams:
        for s in result["streams"]:
            print(s)
        return

    if args.info:
        h = result["header"]
        print(f"File: {result['file']}")
        print(f"Version: {h['version']}")
        print(f"Compressed: {h['compressed']}")
        print(f"Encrypted: {h['encrypted']}")
        print(f"Sections: {result['section_count']}")
        print(f"Streams: {len(result['streams'])}")
        if result["preview"]:
            print(f"Preview: {result['preview'][:100]}...")
        return

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for i, section in enumerate(result["sections"]):
            if i > 0:
                print("\n--- Section Break ---\n")
            print(section)


if __name__ == "__main__":
    main()
