"""Pack a directory back into a DOCX, PPTX, or XLSX file.

Condenses XML whitespace and creates the ZIP-based Office file.

Usage:
    python pack.py <input_directory> <output_file> [--original <file>]

Examples:
    python pack.py unpacked/ output.docx --original input.docx
    python pack.py unpacked/ output.pptx
"""

import argparse
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom


def pack(src_dir: str, dest_file: str, original: str | None = None) -> str:
    """Pack a directory into an Office file."""
    src = Path(src_dir)
    dest = Path(dest_file)

    if not src.is_dir():
        return f"Error: {src_dir} is not a directory"

    if dest.suffix.lower() not in (".docx", ".pptx", ".xlsx"):
        return f"Error: {dest_file} must be .docx, .pptx, or .xlsx"

    try:
        with tempfile.TemporaryDirectory() as tmp:
            staging = Path(tmp) / "content"
            shutil.copytree(src, staging)

            # Condense XML (remove pretty-print whitespace)
            for xml_file in list(staging.rglob("*.xml")) + list(staging.rglob("*.rels")):
                _condense_xml(xml_file)

            # Create ZIP
            dest.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in staging.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(staging))

        return f"Packed {src_dir} → {dest_file}"

    except Exception as e:
        return f"Error: {e}"


def _condense_xml(path: Path) -> None:
    """Remove extra whitespace from XML, preserving text content nodes."""
    try:
        dom = defusedxml.minidom.parseString(path.read_bytes())

        # Remove whitespace-only text nodes (except inside text elements)
        _strip_whitespace_nodes(dom.documentElement)

        path.write_bytes(dom.toxml(encoding="UTF-8"))
    except Exception as e:
        print(f"Warning: Could not condense {path.name}: {e}", file=sys.stderr)


def _strip_whitespace_nodes(element) -> None:
    """Recursively remove whitespace-only text nodes, preserving :t elements."""
    tag = element.tagName if hasattr(element, "tagName") else ""

    # Don't strip inside text-content elements (w:t, a:t, t, etc.)
    if tag.endswith(":t") or tag == "t":
        return

    for child in list(element.childNodes):
        if child.nodeType == child.TEXT_NODE:
            if child.nodeValue and child.nodeValue.strip() == "":
                element.removeChild(child)
        elif child.nodeType == child.ELEMENT_NODE:
            _strip_whitespace_nodes(child)
        elif child.nodeType == child.COMMENT_NODE:
            element.removeChild(child)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pack a directory into an Office file"
    )
    parser.add_argument("input_directory", help="Unpacked Office document directory")
    parser.add_argument("output_file", help="Output file (.docx/.pptx/.xlsx)")
    parser.add_argument("--original", help="Original file for reference (reserved for future validation)")
    args = parser.parse_args()

    msg = pack(args.input_directory, args.output_file, original=args.original)
    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
