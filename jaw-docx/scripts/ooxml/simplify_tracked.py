"""Simplify tracked changes by merging adjacent insertions/deletions from the same author.

When editing DOCX with tracked changes enabled, each edit operation creates
separate <w:ins> or <w:del> elements. This produces verbose redline markup
that is hard to review. This module merges adjacent tracked-change elements
from the same author into single blocks.

Usage:
    python simplify_tracked.py <unpacked_dir> [--original <original.docx>]

Returns dict: {"merged_count": int, "authors": [...]}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


_WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def get_tracked_change_authors(unpacked_dir: str) -> list[str]:
    """Return a deduplicated list of authors from tracked changes."""
    p = Path(unpacked_dir)
    doc = p / "word" / "document.xml"
    if not doc.exists():
        return []

    authors: set[str] = set()
    try:
        tree = ET.parse(doc)  # noqa: S314
        for tag_name in ("ins", "del", "rPrChange", "pPrChange", "sectPrChange"):
            for elem in tree.iter(f"{{{_WNS}}}{tag_name}"):
                author = elem.get(f"{{{_WNS}}}author") or elem.get("w:author")
                if author:
                    authors.add(author)
    except ET.ParseError:
        pass

    return sorted(authors)


def infer_agent_author(
    unpacked_dir: str,
    original_docx: str | None = None,
    default: str = "Agent",
) -> str:
    """Infer which author name was used for agent-generated tracked changes.

    Strategy: find authors present in edited but absent from original.
    Falls back to *default* if no difference found.
    """
    edited_authors = set(get_tracked_change_authors(unpacked_dir))

    if not original_docx or not Path(original_docx).exists():
        # No original — return most common non-obvious author or default
        return edited_authors.pop() if len(edited_authors) == 1 else default

    import tempfile
    import zipfile

    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(original_docx, "r") as zf:
        zf.extractall(tmp)
    original_authors = set(get_tracked_change_authors(tmp))

    new_authors = edited_authors - original_authors
    if len(new_authors) == 1:
        return new_authors.pop()
    return default


def simplify_tracked_changes(unpacked_dir: str) -> dict:
    """Merge adjacent <w:ins>/<w:del> elements from the same author.

    Returns {"merged_count": int, "authors": [...]}
    """
    p = Path(unpacked_dir)
    doc = p / "word" / "document.xml"
    if not doc.exists():
        return {"merged_count": 0, "authors": []}

    try:
        tree = ET.parse(doc)  # noqa: S314
        root = tree.getroot()
    except ET.ParseError:
        return {"merged_count": 0, "authors": []}

    merged = 0

    # Process body and all container elements
    for parent in root.iter():
        children = list(parent)
        i = 0
        while i < len(children) - 1:
            curr = children[i]
            nxt = children[i + 1]

            curr_tag = curr.tag.split("}")[-1] if "}" in curr.tag else curr.tag
            nxt_tag = nxt.tag.split("}")[-1] if "}" in nxt.tag else nxt.tag

            # Only merge same-type tracked changes (ins+ins or del+del)
            if curr_tag not in ("ins", "del") or curr_tag != nxt_tag:
                i += 1
                continue

            # Check same author
            curr_author = curr.get(f"{{{_WNS}}}author") or curr.get("w:author") or ""
            nxt_author = nxt.get(f"{{{_WNS}}}author") or nxt.get("w:author") or ""

            if curr_author != nxt_author:
                i += 1
                continue

            # Merge: move all children from nxt into curr
            for child in list(nxt):
                curr.append(child)

            parent.remove(nxt)
            children = list(parent)
            merged += 1
            # Don't increment — check next neighbor

        # No need to increment here; while loop handles it

    if merged > 0:
        tree.write(doc, xml_declaration=True, encoding="UTF-8")

    authors = get_tracked_change_authors(unpacked_dir)
    return {"merged_count": merged, "authors": authors}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simplify tracked changes in DOCX")
    parser.add_argument("path", help="Unpacked DOCX directory")
    args = parser.parse_args()

    result = simplify_tracked_changes(args.path)
    print(json.dumps(result, indent=2))
