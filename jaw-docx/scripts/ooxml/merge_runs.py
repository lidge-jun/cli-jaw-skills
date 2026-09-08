"""Merge adjacent <w:r> elements with identical formatting.

When editing DOCX XML, each keystroke or edit tool call often creates a new
<w:r> (run) element. This produces bloated XML with many tiny runs.  This
module merges adjacent runs that share the same <w:rPr> (run properties),
combining their text nodes.

Also strips rsid* attributes and <w:proofErr> elements that serve no
purpose in agent-generated content.

Usage:
    python merge_runs.py <unpacked_dir>

Returns dict: {"merged_count": int, "files_modified": int}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


_WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_RSID_ATTRS = {"rsidR", "rsidRPr", "rsidRDefault", "rsidP", "rsidDel", "rsidSect"}


def _serialize_rpr(rpr_elem: ET.Element | None) -> str:
    """Serialize <w:rPr> to a canonical string for comparison."""
    if rpr_elem is None:
        return ""
    # Strip rsid attributes from comparison
    parts: list[str] = []
    for child in rpr_elem:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        attribs = {k: v for k, v in child.attrib.items() if k.split("}")[-1] not in _RSID_ATTRS}
        parts.append(f"{tag}:{sorted(attribs.items())}")
    return "|".join(sorted(parts))


def _strip_rsid(elem: ET.Element) -> None:
    """Remove rsid* attributes from an element."""
    to_remove = [k for k in elem.attrib if k.split("}")[-1] in _RSID_ATTRS]
    for k in to_remove:
        del elem.attrib[k]


def _remove_proof_errors(parent: ET.Element) -> int:
    """Remove <w:proofErr> elements. Returns count removed."""
    count = 0
    for child in list(parent):
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "proofErr":
            parent.remove(child)
            count += 1
    return count


def merge_adjacent_runs(unpacked_dir: str) -> dict:
    """Merge adjacent <w:r> elements with identical <w:rPr> in all document XML files.

    Returns {"merged_count": int, "files_modified": int, "proof_errors_removed": int}
    """
    p = Path(unpacked_dir)
    word_dir = p / "word"
    if not word_dir.is_dir():
        return {"merged_count": 0, "files_modified": 0, "proof_errors_removed": 0}

    total_merged = 0
    total_proof = 0
    files_modified = 0

    # Process document.xml and any header/footer XMLs
    xml_files = list(word_dir.glob("document*.xml")) + \
                list(word_dir.glob("header*.xml")) + \
                list(word_dir.glob("footer*.xml"))

    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)  # noqa: S314
            root = tree.getroot()
            file_merged = 0
            file_proof = 0

            # Process all paragraphs
            for para in root.iter(f"{{{_WNS}}}p"):
                # Strip rsid from paragraph
                _strip_rsid(para)

                # Remove proofErr from paragraph
                file_proof += _remove_proof_errors(para)

                # Collect runs in order
                children = list(para)
                i = 0
                while i < len(children) - 1:
                    curr = children[i]
                    nxt = children[i + 1]

                    curr_tag = curr.tag.split("}")[-1] if "}" in curr.tag else curr.tag
                    nxt_tag = nxt.tag.split("}")[-1] if "}" in nxt.tag else nxt.tag

                    if curr_tag != "r" or nxt_tag != "r":
                        i += 1
                        continue

                    # Strip rsid from runs
                    _strip_rsid(curr)
                    _strip_rsid(nxt)

                    # Compare rPr
                    curr_rpr = curr.find(f"{{{_WNS}}}rPr")
                    nxt_rpr = nxt.find(f"{{{_WNS}}}rPr")

                    if _serialize_rpr(curr_rpr) == _serialize_rpr(nxt_rpr):
                        # Merge text from nxt into curr
                        curr_t = curr.find(f"{{{_WNS}}}t")
                        nxt_t = nxt.find(f"{{{_WNS}}}t")

                        if curr_t is not None and nxt_t is not None:
                            curr_t.text = (curr_t.text or "") + (nxt_t.text or "")
                            # Ensure space preservation
                            curr_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                            # Remove the merged run
                            para.remove(nxt)
                            children = list(para)
                            file_merged += 1
                            continue  # Don't increment i — check new neighbor
                    i += 1

            if file_merged > 0 or file_proof > 0:
                tree.write(xml_file, xml_declaration=True, encoding="UTF-8")
                files_modified += 1
                total_merged += file_merged
                total_proof += file_proof

        except ET.ParseError:
            pass

    return {
        "merged_count": total_merged,
        "files_modified": files_modified,
        "proof_errors_removed": total_proof,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge adjacent runs in DOCX XML")
    parser.add_argument("path", help="Unpacked DOCX directory")
    args = parser.parse_args()

    result = merge_adjacent_runs(args.path)
    print(json.dumps(result, indent=2))
