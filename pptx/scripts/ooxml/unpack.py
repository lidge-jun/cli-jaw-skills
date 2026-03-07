"""Unpack Office files (DOCX, PPTX, XLSX) for XML editing.

Extracts the ZIP archive and pretty-prints all XML files for human-readable editing.
Smart quotes are converted to XML entities for safe XML manipulation.

Usage:
    python unpack.py <office_file> <output_dir>

Examples:
    python unpack.py document.docx unpacked/
    python unpack.py presentation.pptx unpacked/
"""

import argparse
import sys
import zipfile
from pathlib import Path

import defusedxml.minidom

SMART_QUOTE_MAP = {
    "\u201c": "&#x201C;",  # left double quote
    "\u201d": "&#x201D;",  # right double quote
    "\u2018": "&#x2018;",  # left single quote
    "\u2019": "&#x2019;",  # right single quote
}


def unpack(src: str, dest: str) -> str:
    """Extract an Office file and pretty-print its XML contents."""
    src_path = Path(src)
    dest_path = Path(dest)

    if not src_path.exists():
        return f"Error: {src} does not exist"

    if src_path.suffix.lower() not in (".docx", ".pptx", ".xlsx"):
        return f"Error: {src} must be a .docx, .pptx, or .xlsx file"

    try:
        dest_path.mkdir(parents=True, exist_ok=True)

        # Zip bomb protection
        MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500 MB
        MAX_FILE_COUNT = 10_000
        MAX_SINGLE_FILE = 100 * 1024 * 1024  # 100 MB

        with zipfile.ZipFile(src_path, "r") as zf:
            total_size = sum(info.file_size for info in zf.infolist())
            file_count = len(zf.infolist())
            compressed_size = sum(info.compress_size for info in zf.infolist()) or 1

            if total_size > MAX_TOTAL_SIZE:
                return f"Error: archive uncompressed size ({total_size:,} bytes) exceeds limit ({MAX_TOTAL_SIZE:,} bytes)"
            if file_count > MAX_FILE_COUNT:
                return f"Error: archive contains {file_count:,} files (limit: {MAX_FILE_COUNT:,})"
            if total_size / compressed_size > 100:
                return f"Error: suspicious compression ratio ({total_size / compressed_size:.0f}x)"
            for info in zf.infolist():
                if info.file_size > MAX_SINGLE_FILE:
                    return f"Error: file {info.filename} ({info.file_size:,} bytes) exceeds single-file limit"

            zf.extractall(dest_path)

        xml_count = 0
        for xml_file in _iter_xml_files(dest_path):
            _pretty_print(xml_file)
            _replace_smart_quotes(xml_file)
            xml_count += 1

        return f"Unpacked {src} → {dest} ({xml_count} XML files processed)"

    except zipfile.BadZipFile:
        return f"Error: {src} is not a valid ZIP/Office file"
    except Exception as e:
        return f"Error: {e}"


def _iter_xml_files(root: Path):
    """Yield all .xml and .rels files under root."""
    yield from root.rglob("*.xml")
    yield from root.rglob("*.rels")


def _pretty_print(path: Path) -> None:
    """Reformat XML with indentation for readability."""
    try:
        raw = path.read_bytes()
        dom = defusedxml.minidom.parseString(raw)
        path.write_bytes(dom.toprettyxml(indent="  ", encoding="utf-8"))
    except Exception:
        pass  # skip non-parseable files silently


def _replace_smart_quotes(path: Path) -> None:
    """Convert Unicode smart quotes to XML entities."""
    try:
        text = path.read_text(encoding="utf-8")
        changed = False
        for char, entity in SMART_QUOTE_MAP.items():
            if char in text:
                text = text.replace(char, entity)
                changed = True
        if changed:
            path.write_text(text, encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Unpack an Office file for XML editing"
    )
    parser.add_argument("input_file", help="Office file to unpack (.docx/.pptx/.xlsx)")
    parser.add_argument("output_directory", help="Directory to extract into")
    args = parser.parse_args()

    msg = unpack(args.input_file, args.output_directory)
    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
