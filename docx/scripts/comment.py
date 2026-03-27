"""Add comments to a DOCX file at specified text locations.

Inserts W3C-compliant OOXML comment annotations, handling all required
relationship and content-type entries.

Usage:
    python comment.py <input.docx> <output.docx> --author "Name" --text "Comment text" --anchor "target text"
    python comment.py <input.docx> <output.docx> --json comments.json
"""

import argparse
import copy
import json
import re
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import defusedxml.minidom

# OOXML namespace URIs
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

COMMENTS_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
COMMENTS_EXT_REL_TYPE = "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"


def add_comments(
    input_path: str,
    output_path: str,
    comments: list[dict],
) -> str:
    """Add comments to a DOCX file.

    Each comment dict should have:
        - author: str
        - text: str
        - anchor: str (text to search for in the document)
    """
    src = Path(input_path).resolve()
    dst = Path(output_path).resolve()

    if not src.exists():
        return f"Error: {input_path} does not exist"

    try:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            with zipfile.ZipFile(src, "r") as zf:
                zf.extractall(tmp_path)

            # Load or create comments.xml
            comments_xml_path = tmp_path / "word" / "comments.xml"
            if comments_xml_path.exists():
                comments_dom = defusedxml.minidom.parseString(
                    comments_xml_path.read_bytes()
                )
                next_id = _get_max_comment_id(comments_dom) + 1
            else:
                comments_dom = _create_comments_xml()
                next_id = 1

            # Load document.xml
            doc_path = tmp_path / "word" / "document.xml"
            if not doc_path.exists():
                return "Error: not a valid DOCX (missing word/document.xml)"
            doc_dom = defusedxml.minidom.parseString(doc_path.read_bytes())

            added = 0
            for comment_data in comments:
                author = comment_data.get("author", "Agent")
                text = comment_data.get("text", "")
                anchor = comment_data.get("anchor", "")

                if not anchor or not text:
                    continue

                comment_id = next_id
                next_id += 1

                # Add comment element to comments.xml
                _add_comment_element(comments_dom, comment_id, author, text)

                # Insert comment markers in document.xml
                if _insert_comment_markers(doc_dom, comment_id, anchor):
                    added += 1

            # Write modified XMLs
            comments_xml_path.write_bytes(comments_dom.toxml(encoding="UTF-8"))
            doc_path.write_bytes(doc_dom.toxml(encoding="UTF-8"))

            # Ensure relationships and content types
            _ensure_rels(tmp_path)
            _ensure_content_types(tmp_path)

            # Repack
            dst.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in tmp_path.rglob("*"):
                    if f.is_file():
                        zf.write(f, f.relative_to(tmp_path))

        return f"Added {added}/{len(comments)} comments → {output_path}"

    except Exception as e:
        return f"Error: {e}"


def _create_comments_xml():
    """Create a new empty comments.xml DOM."""
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        "</w:comments>"
    )
    return defusedxml.minidom.parseString(xml)


def _get_max_comment_id(dom) -> int:
    """Get the highest existing comment ID."""
    max_id = 0
    for comment in dom.getElementsByTagNameNS(NS["w"], "comment"):
        cid = comment.getAttributeNS(NS["w"], "id")
        if cid:
            max_id = max(max_id, int(cid))
    return max_id


def _add_comment_element(dom, comment_id: int, author: str, text: str) -> None:
    """Add a w:comment element to the comments DOM."""
    root = dom.documentElement
    comment = dom.createElementNS(NS["w"], "w:comment")
    comment.setAttributeNS(NS["w"], "w:id", str(comment_id))
    comment.setAttributeNS(NS["w"], "w:author", author)
    comment.setAttributeNS(NS["w"], "w:initials", author[:2].upper())
    comment.setAttributeNS(
        NS["w"], "w:date", datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # Create paragraph with text
    p = dom.createElementNS(NS["w"], "w:p")
    r = dom.createElementNS(NS["w"], "w:r")
    t = dom.createElementNS(NS["w"], "w:t")
    t.appendChild(dom.createTextNode(text))
    r.appendChild(t)
    p.appendChild(r)
    comment.appendChild(p)

    root.appendChild(comment)


def _insert_comment_markers(dom, comment_id: int, anchor_text: str) -> bool:
    """Insert commentRangeStart/End markers, handling text split across runs.

    Strategy:
    1. Build a text map per paragraph (concatenating all w:t in all w:r)
    2. Find the character offset of anchor_text in the paragraph text
    3. Map char offset back to specific w:r/w:t nodes
    4. Insert commentRangeStart before first run, commentRangeEnd after last
    """
    body = dom.getElementsByTagNameNS(NS["w"], "body")
    if not body:
        return False

    for para in dom.getElementsByTagNameNS(NS["w"], "p"):
        runs_map, idx = _find_anchor_span(para, anchor_text)
        if idx == -1:
            continue

        anchor_end = idx + len(anchor_text)
        first_entry, last_entry = _find_span_entries(runs_map, idx, anchor_end)
        if first_entry is None or last_entry is None:
            continue

        if anchor_end < last_entry[4]:
            if not _entry_supports_split(last_entry):
                continue
            _split_run_at(dom, last_entry[1], last_entry[2], anchor_end - last_entry[3])

        if idx > first_entry[3]:
            if not _entry_supports_split(first_entry):
                continue
            _split_run_at(dom, first_entry[1], first_entry[2], idx - first_entry[3])

        runs_map, idx = _find_anchor_span(para, anchor_text)
        if idx == -1:
            continue
        anchor_end = idx + len(anchor_text)
        first_entry, last_entry = _find_span_entries(runs_map, idx, anchor_end)
        if first_entry is None or last_entry is None:
            continue

        first_container = first_entry[0]
        last_container = last_entry[0]

        # 3. Insert markers
        range_start = dom.createElementNS(NS["w"], "w:commentRangeStart")
        range_start.setAttributeNS(NS["w"], "w:id", str(comment_id))
        range_end = dom.createElementNS(NS["w"], "w:commentRangeEnd")
        range_end.setAttributeNS(NS["w"], "w:id", str(comment_id))
        ref_run = dom.createElementNS(NS["w"], "w:r")
        ref = dom.createElementNS(NS["w"], "w:commentReference")
        ref.setAttributeNS(NS["w"], "w:id", str(comment_id))
        ref_run.appendChild(ref)

        para.insertBefore(range_start, first_container)
        if last_container.nextSibling:
            para.insertBefore(range_end, last_container.nextSibling)
            para.insertBefore(ref_run, range_end.nextSibling)
        else:
            para.appendChild(range_end)
            para.appendChild(ref_run)
        return True

    return False


def _find_anchor_span(para, anchor_text: str):
    """Return paragraph run map and anchor start offset, or -1 if absent."""
    runs_map = []
    offset = 0
    for container in para.childNodes:
        if getattr(container, "localName", None) not in ("r", "hyperlink"):
            continue
        if container.namespaceURI != NS["w"]:
            continue
        for run, t in _iter_text_nodes(container):
            text = t.childNodes[0].nodeValue if t.childNodes else ""
            runs_map.append((container, run, t, offset, offset + len(text)))
            offset += len(text)

    para_text = "".join(
        entry[2].childNodes[0].nodeValue if entry[2].childNodes else ""
        for entry in runs_map
    )
    return runs_map, para_text.find(anchor_text)


def _find_span_entries(runs_map, start_idx: int, end_idx: int):
    """Return first/last entries intersecting [start_idx, end_idx)."""
    first_entry = last_entry = None
    for entry in runs_map:
        _, _, _, start, end = entry
        if start < end_idx and end > start_idx:
            if first_entry is None:
                first_entry = entry
            last_entry = entry
    return first_entry, last_entry


def _iter_text_nodes(container):
    """Yield (run, w:t) pairs in document order for a paragraph inline container."""
    if getattr(container, "localName", None) == "r" and container.namespaceURI == NS["w"]:
        for child in container.childNodes:
            if getattr(child, "localName", None) == "t" and child.namespaceURI == NS["w"]:
                yield container, child
        return

    for run in container.getElementsByTagNameNS(NS["w"], "r"):
        for child in run.childNodes:
            if getattr(child, "localName", None) == "t" and child.namespaceURI == NS["w"]:
                yield run, child


def _set_text(dom, t_elem, text: str) -> None:
    """Replace the text content of a w:t node."""
    while t_elem.firstChild:
        t_elem.removeChild(t_elem.firstChild)
    if text:
        t_elem.appendChild(dom.createTextNode(text))


def _text_child_index(run, target_t) -> int:
    """Get the ordinal of a w:t child within a run."""
    idx = 0
    for child in run.childNodes:
        if getattr(child, "localName", None) == "t" and child.namespaceURI == NS["w"]:
            if child is target_t:
                return idx
            idx += 1
    raise ValueError("target text node not found in run")


def _text_child_by_index(run, index: int):
    """Return the nth w:t child within a run."""
    idx = 0
    for child in run.childNodes:
        if getattr(child, "localName", None) == "t" and child.namespaceURI == NS["w"]:
            if idx == index:
                return child
            idx += 1
    raise ValueError("text child index out of range")


def _split_run_at(dom, run, t_elem, split_offset: int):
    """Split a run's target text node into left/right runs at split_offset."""
    text = t_elem.childNodes[0].nodeValue if t_elem.childNodes else ""
    if split_offset <= 0 or split_offset >= len(text):
        return run, None

    text_index = _text_child_index(run, t_elem)
    new_run = run.cloneNode(deep=True)
    new_t = _text_child_by_index(new_run, text_index)

    _set_text(dom, t_elem, text[:split_offset])
    _set_text(dom, new_t, text[split_offset:])

    parent = run.parentNode
    if run.nextSibling:
        parent.insertBefore(new_run, run.nextSibling)
    else:
        parent.appendChild(new_run)
    return run, new_run


def _entry_supports_split(entry) -> bool:
    """Return True if the entry can be split without crossing a non-run container."""
    container, run, _, _, _ = entry
    return container is run


def _ensure_rels(tmp_path: Path) -> None:
    """Ensure word/_rels/document.xml.rels has the comments relationship."""
    rels_path = tmp_path / "word" / "_rels" / "document.xml.rels"
    rels_path.parent.mkdir(parents=True, exist_ok=True)

    if rels_path.exists():
        dom = defusedxml.minidom.parseString(rels_path.read_bytes())
    else:
        dom = defusedxml.minidom.parseString(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            "</Relationships>"
        )

    root = dom.documentElement

    # Check if comments relationship exists
    has_comments = False
    for rel in root.getElementsByTagName("Relationship"):
        if rel.getAttribute("Type") == COMMENTS_REL_TYPE:
            has_comments = True
            break

    if not has_comments:
        rel = dom.createElement("Relationship")
        rel.setAttribute("Id", f"rId{uuid.uuid4().hex[:8]}")
        rel.setAttribute("Type", COMMENTS_REL_TYPE)
        rel.setAttribute("Target", "comments.xml")
        root.appendChild(rel)

    rels_path.write_bytes(dom.toxml(encoding="UTF-8"))


def _ensure_content_types(tmp_path: Path) -> None:
    """Ensure [Content_Types].xml includes comments content type."""
    ct_path = tmp_path / "[Content_Types].xml"
    if not ct_path.exists():
        return

    dom = defusedxml.minidom.parseString(ct_path.read_bytes())
    root = dom.documentElement

    # Check for comments override
    target = "/word/comments.xml"
    for override in root.getElementsByTagName("Override"):
        if override.getAttribute("PartName") == target:
            return  # already exists

    override = dom.createElement("Override")
    override.setAttribute("PartName", target)
    override.setAttribute(
        "ContentType",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
    )
    root.appendChild(override)

    ct_path.write_bytes(dom.toxml(encoding="UTF-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add comments to a DOCX file")
    parser.add_argument("input_file", help="Input DOCX")
    parser.add_argument("output_file", help="Output DOCX with comments")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--json",
        help="JSON file with array of {author, text, anchor} objects",
    )
    group.add_argument("--text", help="Comment text (use with --author and --anchor)")

    parser.add_argument("--author", default="Agent", help="Comment author name")
    parser.add_argument("--anchor", help="Text to attach the comment to")

    args = parser.parse_args()

    if args.json:
        with open(args.json) as f:
            comments_list = json.load(f)
    else:
        if not args.anchor:
            print("Error: --anchor is required when using --text", file=sys.stderr)
            sys.exit(1)
        comments_list = [{"author": args.author, "text": args.text, "anchor": args.anchor}]

    msg = add_comments(args.input_file, args.output_file, comments_list)
    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
