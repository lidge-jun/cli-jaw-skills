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
    """Insert commentRangeStart/End markers around matching text in document."""
    body = dom.getElementsByTagNameNS(NS["w"], "body")
    if not body:
        return False

    # Find text nodes matching anchor
    for t_elem in dom.getElementsByTagNameNS(NS["w"], "t"):
        if t_elem.childNodes and anchor_text in t_elem.childNodes[0].nodeValue:
            # Get the parent run and paragraph
            run = t_elem.parentNode  # w:r
            para = run.parentNode  # w:p

            # Create markers
            range_start = dom.createElementNS(NS["w"], "w:commentRangeStart")
            range_start.setAttributeNS(NS["w"], "w:id", str(comment_id))

            range_end = dom.createElementNS(NS["w"], "w:commentRangeEnd")
            range_end.setAttributeNS(NS["w"], "w:id", str(comment_id))

            # Comment reference run
            ref_run = dom.createElementNS(NS["w"], "w:r")
            ref = dom.createElementNS(NS["w"], "w:commentReference")
            ref.setAttributeNS(NS["w"], "w:id", str(comment_id))
            ref_run.appendChild(ref)

            # Insert markers
            para.insertBefore(range_start, run)
            if run.nextSibling:
                para.insertBefore(range_end, run.nextSibling)
                para.insertBefore(ref_run, range_end.nextSibling)
            else:
                para.appendChild(range_end)
                para.appendChild(ref_run)

            return True

    return False


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
