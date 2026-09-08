"""Validate tracked changes by diffing text with and without agent's edits.

Compares the "accepted all changes" text against the original document text
to verify that tracked-change markup accurately represents the intended
modifications. Uses Python's difflib for portable word-level diffing (no
git dependency).

Usage:
    python redline_diff.py <unpacked_dir> <original.docx> [--author Agent]

Returns dict: {"passed": bool, "diff": str | None, "stats": {...}}
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


_WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _extract_text(doc_xml: Path) -> str:
    """Extract plain text from a document.xml, preserving paragraph breaks."""
    if not doc_xml.exists():
        return ""
    try:
        tree = ET.parse(doc_xml)  # noqa: S314
        lines: list[str] = []
        for para in tree.iter(f"{{{_WNS}}}p"):
            parts: list[str] = []
            for t_elem in para.iter(f"{{{_WNS}}}t"):
                if t_elem.text:
                    parts.append(t_elem.text)
            lines.append("".join(parts))
        return "\n".join(lines)
    except ET.ParseError:
        return ""


def _extract_text_without_author(doc_xml: Path, author: str) -> str:
    """Extract text, treating agent's insertions as absent and deletions as present.

    This reconstructs the "original" text as it would appear if the agent's
    tracked changes were rejected.
    """
    if not doc_xml.exists():
        return ""
    try:
        tree = ET.parse(doc_xml)  # noqa: S314
        lines: list[str] = []

        for para in tree.iter(f"{{{_WNS}}}p"):
            parts: list[str] = []
            _collect_text_excluding_author(para, author, parts)
            lines.append("".join(parts))

        return "\n".join(lines)
    except ET.ParseError:
        return ""


def _collect_text_excluding_author(
    elem: ET.Element, author: str, parts: list[str]
) -> None:
    """Recursively collect text, skipping agent's insertions, keeping agent's deletions."""
    tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
    elem_author = elem.get(f"{{{_WNS}}}author") or elem.get("w:author") or ""

    if tag == "ins" and elem_author == author:
        # Agent's insertion — skip entirely (reject it)
        return

    if tag == "del" and elem_author == author:
        # Agent's deletion — include the deleted text (restore it)
        for dt in elem.iter(f"{{{_WNS}}}delText"):
            if dt.text:
                parts.append(dt.text)
        return

    # For regular elements, collect <w:t> text at this level
    if tag == "t":
        if elem.text:
            parts.append(elem.text)
        return

    # Recurse into children
    for child in elem:
        _collect_text_excluding_author(child, author, parts)


def _extract_text_with_author(doc_xml: Path, author: str) -> str:
    """Extract text as it would appear if the agent's changes were accepted.

    Agent's insertions are included, agent's deletions are excluded.
    """
    if not doc_xml.exists():
        return ""
    try:
        tree = ET.parse(doc_xml)  # noqa: S314
        lines: list[str] = []

        for para in tree.iter(f"{{{_WNS}}}p"):
            parts: list[str] = []
            _collect_text_including_author(para, author, parts)
            lines.append("".join(parts))

        return "\n".join(lines)
    except ET.ParseError:
        return ""


def _collect_text_including_author(
    elem: ET.Element, author: str, parts: list[str]
) -> None:
    """Recursively collect text, including agent's insertions, excluding agent's deletions."""
    tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
    elem_author = elem.get(f"{{{_WNS}}}author") or elem.get("w:author") or ""

    if tag == "del" and elem_author == author:
        # Agent's deletion — skip (accept the deletion)
        return

    if tag == "del":
        # Another author's deletion — include deleted text
        for dt in elem.iter(f"{{{_WNS}}}delText"):
            if dt.text:
                parts.append(dt.text)
        return

    if tag == "t":
        if elem.text:
            parts.append(elem.text)
        return

    if tag == "delText":
        return  # Only collected under explicit <w:del> handling

    for child in elem:
        _collect_text_including_author(child, author, parts)


def revision_stats(unpacked_dir: str) -> dict:
    """Return per-author insertion/deletion word counts.

    Returns {"authors": {"AuthorName": {"insertions": N, "deletions": N}, ...}}
    """
    p = Path(unpacked_dir)
    doc = p / "word" / "document.xml"
    if not doc.exists():
        return {"authors": {}}

    stats: dict[str, dict[str, int]] = {}

    try:
        tree = ET.parse(doc)  # noqa: S314

        for ins in tree.iter(f"{{{_WNS}}}ins"):
            author = ins.get(f"{{{_WNS}}}author") or ins.get("w:author") or "Unknown"
            if author not in stats:
                stats[author] = {"insertions": 0, "deletions": 0}
            words = sum(
                len((t.text or "").split()) for t in ins.iter(f"{{{_WNS}}}t")
            )
            stats[author]["insertions"] += words

        for del_elem in tree.iter(f"{{{_WNS}}}del"):
            author = del_elem.get(f"{{{_WNS}}}author") or del_elem.get("w:author") or "Unknown"
            if author not in stats:
                stats[author] = {"insertions": 0, "deletions": 0}
            words = sum(
                len((t.text or "").split()) for t in del_elem.iter(f"{{{_WNS}}}delText")
            )
            stats[author]["deletions"] += words

    except ET.ParseError:
        pass

    return {"authors": stats}


def validate_tracked_changes(
    unpacked_dir: str,
    original_docx: str,
    author: str = "Agent",
) -> dict:
    """Verify tracked changes correctness by comparing original vs accepted text.

    Returns {"passed": bool, "diff": str | None, "stats": {...}}
    """
    p = Path(unpacked_dir)
    doc = p / "word" / "document.xml"

    # Extract "rejected" text (original view) from the edited document
    rejected_text = _extract_text_without_author(doc, author)

    # Extract text from original file
    orig_path = Path(original_docx)
    if orig_path.is_file() and orig_path.suffix.lower() == ".docx":
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(orig_path, "r") as zf:
            zf.extractall(tmp)
        original_text = _extract_text(Path(tmp) / "word" / "document.xml")
    elif orig_path.is_dir():
        original_text = _extract_text(orig_path / "word" / "document.xml")
    else:
        return {"passed": False, "diff": None, "stats": {"error": f"Cannot read original: {original_docx}"}}

    # Compare
    orig_lines = original_text.splitlines(keepends=True)
    rejected_lines = rejected_text.splitlines(keepends=True)

    diff_lines = list(difflib.unified_diff(
        orig_lines, rejected_lines,
        fromfile="original", tofile="rejected-edits",
        lineterm=""
    ))

    diff_text = "\n".join(diff_lines) if diff_lines else None
    passed = len(diff_lines) == 0

    stats = revision_stats(unpacked_dir)
    stats["original_paragraphs"] = len(orig_lines)
    stats["edited_paragraphs"] = len(rejected_lines)

    return {
        "passed": passed,
        "diff": diff_text,
        "stats": stats,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate tracked changes via diff")
    parser.add_argument("unpacked_dir", help="Unpacked edited DOCX directory")
    parser.add_argument("original", help="Original DOCX file or unpacked directory")
    parser.add_argument("--author", default="Agent", help="Author name for agent changes")
    args = parser.parse_args()

    result = validate_tracked_changes(args.unpacked_dir, args.original, args.author)
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["passed"] else 1)
