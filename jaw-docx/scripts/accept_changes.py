"""Accept all tracked changes in a DOCX file via direct OOXML processing.

This implementation intentionally uses the OOXML fallback path because the
LibreOffice macro module is not provisioned by this script. The output is
verified with a post-assertion pass before success is reported.

Usage:
    python accept_changes.py <input.docx> <output.docx>
"""

import argparse
import sys
import tempfile
from pathlib import Path

# Revision markup tags that indicate tracked changes
REVISION_TAGS = (
    "ins", "del", "rPrChange", "pPrChange",
    "tblPrChange", "trPrChange", "tcPrChange", "sectPrChange",
)


def accept_changes(input_path: str, output_path: str) -> str:
    """Accept all tracked changes in a DOCX file."""
    src = Path(input_path).resolve()
    dst = Path(output_path).resolve()

    if not src.exists():
        return f"Error: {input_path} does not exist"

    if not src.suffix.lower() == ".docx":
        return f"Error: {input_path} must be a .docx file"

    try:
        return _fallback_accept(src, dst)

    except Exception as e:
        return f"Error: {e}"


def _fallback_accept(src: Path, dst: Path) -> str:
    """Fallback: process ALL word/*.xml parts, not just document.xml.

    Removes revision markup elements (w:ins, w:del, w:rPrChange, etc.)
    from document.xml, headers, footers, endnotes, and footnotes.
    """
    import zipfile

    import defusedxml.minidom

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        with zipfile.ZipFile(src, "r") as zf:
            zf.extractall(tmp_path)

        word_dir = tmp_path / "word"
        if not word_dir.is_dir():
            return "Error: not a valid DOCX (missing word/ directory)"

        # Process ALL xml files in word/ (document, headers, footers, etc.)
        for xml_path in word_dir.glob("*.xml"):
            try:
                dom = defusedxml.minidom.parseString(xml_path.read_bytes())
            except Exception:
                continue

            modified = False

            # Accept insertions: unwrap w:ins (keep children)
            for ins in list(dom.getElementsByTagNameNS("*", "ins")):
                parent = ins.parentNode
                for child in list(ins.childNodes):
                    parent.insertBefore(child, ins)
                parent.removeChild(ins)
                modified = True

            # Accept deletions: remove w:del entirely
            for del_elem in list(dom.getElementsByTagNameNS("*", "del")):
                del_elem.parentNode.removeChild(del_elem)
                modified = True

            # Remove format change markers
            for tag in REVISION_TAGS[2:]:
                for elem in list(dom.getElementsByTagNameNS("*", tag)):
                    elem.parentNode.removeChild(elem)
                    modified = True

            if modified:
                xml_path.write_bytes(dom.toxml(encoding="UTF-8"))

        # Repack
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in tmp_path.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(tmp_path))

    # Post-assertion: verify output is clean
    residue = _count_revision_tags(dst)
    if residue > 0:
        return f"Error: {residue} revision tag(s) still remain after accept"
    return f"Accepted all tracked changes: {src} → {dst}"


def _count_revision_tags(docx_path: Path) -> int:
    """Count remaining revision tags in all word/*.xml parts. Returns 0 if clean."""
    import zipfile

    import defusedxml.minidom

    count = 0
    with zipfile.ZipFile(docx_path, "r") as zf:
        for name in zf.namelist():
            if not name.startswith("word/") or not name.endswith(".xml"):
                continue
            try:
                dom = defusedxml.minidom.parseString(zf.read(name))
                for tag in REVISION_TAGS:
                    count += len(dom.getElementsByTagNameNS("*", tag))
            except Exception:
                continue
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Accept all tracked changes in a DOCX file"
    )
    parser.add_argument("input_file", help="Input DOCX with tracked changes")
    parser.add_argument("output_file", help="Output DOCX with changes accepted")
    args = parser.parse_args()

    msg = accept_changes(args.input_file, args.output_file)
    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
