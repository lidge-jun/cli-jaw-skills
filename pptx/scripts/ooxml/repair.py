"""Auto-repair common OOXML structural issues.

Operates on unpacked directories. Repairs are non-destructive — they only
fix known-safe issues (whitespace attrs, ID range, orphan rels, Content_Types).

Usage:
    python repair.py <unpacked_dir> [--dry-run]

Returns dict: {"repaired": int, "details": [...]}
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


def repair(path: str, *, dry_run: bool = False) -> dict:
    """Run all repair functions on an unpacked OOXML directory.

    Returns {"repaired": int, "details": [...]}
    """
    p = Path(path)
    if not p.is_dir():
        return {"repaired": 0, "details": [f"Not a directory: {path}"]}

    details: list[str] = []

    details.extend(repair_whitespace(p, dry_run=dry_run))
    details.extend(repair_durable_ids(p, dry_run=dry_run))
    details.extend(repair_orphan_rels(p, dry_run=dry_run))
    details.extend(repair_content_types(p, dry_run=dry_run))

    return {"repaired": len(details), "details": details}


def repair_whitespace(unpacked: Path, *, dry_run: bool = False) -> list[str]:
    """Add xml:space='preserve' to <w:t> elements with leading/trailing spaces."""
    details: list[str] = []
    wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ns_space = "{http://www.w3.org/XML/1998/namespace}space"

    for xml_file in unpacked.rglob("*.xml"):
        try:
            tree = ET.parse(xml_file)  # noqa: S314
            modified = False
            for t_elem in tree.iter(f"{{{wns}}}t"):
                text = t_elem.text or ""
                if text != text.strip() or "  " in text:
                    if t_elem.get(ns_space) != "preserve":
                        if not dry_run:
                            t_elem.set(ns_space, "preserve")
                        modified = True
                        rel = xml_file.relative_to(unpacked)
                        details.append(f"Added xml:space='preserve' in {rel}")
            if modified and not dry_run:
                tree.write(xml_file, xml_declaration=True, encoding="UTF-8")
        except ET.ParseError:
            pass

    return details


def repair_durable_ids(unpacked: Path, *, dry_run: bool = False) -> list[str]:
    """Replace durableId/paraId values that exceed their allowed range."""
    details: list[str] = []
    doc = unpacked / "word" / "document.xml"
    if not doc.exists():
        return details

    try:
        tree = ET.parse(doc)  # noqa: S314
        w14 = "http://schemas.microsoft.com/office/word/2010/wordml"
        wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        modified = False

        for elem in tree.iter():
            for ns in (w14, wns):
                para_id = elem.get(f"{{{ns}}}paraId")
                if para_id:
                    try:
                        val = int(para_id, 16)
                        if val >= 0x80000000:
                            new_id = f"{random.randint(0x00000001, 0x7FFFFFFF):08X}"
                            if not dry_run:
                                elem.set(f"{{{ns}}}paraId", new_id)
                            details.append(f"Repaired paraId {para_id} → {new_id}")
                            modified = True
                    except ValueError:
                        pass

                dur_id = elem.get(f"{{{ns}}}durableId")
                if dur_id:
                    try:
                        val = int(dur_id) if dur_id.isdigit() else int(dur_id, 16)
                        if val >= 0x7FFFFFFF:
                            new_id = str(random.randint(1, 0x7FFFFFFE))
                            if not dry_run:
                                elem.set(f"{{{ns}}}durableId", new_id)
                            details.append(f"Repaired durableId {dur_id} → {new_id}")
                            modified = True
                    except ValueError:
                        pass

        if modified and not dry_run:
            tree.write(doc, xml_declaration=True, encoding="UTF-8")
    except ET.ParseError:
        pass

    return details


def repair_orphan_rels(unpacked: Path, *, dry_run: bool = False) -> list[str]:
    """Remove Relationship elements pointing to non-existent files."""
    details: list[str] = []

    for rels_file in unpacked.rglob("*.rels"):
        try:
            tree = ET.parse(rels_file)  # noqa: S314
            root = tree.getroot()
            rels_dir = rels_file.parent.parent
            to_remove = []

            for rel in list(root):
                tag = rel.tag.split("}")[-1] if "}" in rel.tag else rel.tag
                if tag != "Relationship":
                    continue
                target = rel.get("Target", "")
                if not target or target.startswith("http://") or target.startswith("https://"):
                    continue
                target_clean = target.split("#")[0]
                if not target_clean:
                    continue
                target_path = (rels_dir / target_clean).resolve()
                if not target_path.exists():
                    to_remove.append(rel)
                    rid = rel.get("Id", "?")
                    rel_path = rels_file.relative_to(unpacked)
                    details.append(f"Removed orphan relationship {rid} → '{target}' in {rel_path}")

            if to_remove and not dry_run:
                for rel in to_remove:
                    root.remove(rel)
                tree.write(rels_file, xml_declaration=True, encoding="UTF-8")
        except ET.ParseError:
            pass

    return details


def repair_content_types(unpacked: Path, *, dry_run: bool = False) -> list[str]:
    """Add missing Override entries in [Content_Types].xml for existing files."""
    ct_path = unpacked / "[Content_Types].xml"
    if not ct_path.exists():
        return []

    details: list[str] = []

    # Map extensions to default content types
    _EXT_TYPES = {
        ".xml": "application/xml",
        ".rels": "application/vnd.openxmlformats-package.relationships+xml",
        ".png": "image/png",
        ".jpeg": "image/jpeg",
        ".jpg": "image/jpeg",
        ".gif": "image/gif",
        ".emf": "image/x-emf",
        ".wmf": "image/x-wmf",
    }

    try:
        tree = ET.parse(ct_path)  # noqa: S314
        root = tree.getroot()
        ns = "http://schemas.openxmlformats.org/package/2006/content-types"

        # Collect already-declared overrides and defaults
        overrides = set()
        for ov in root.findall(f"{{{ns}}}Override"):
            overrides.add(ov.get("PartName", ""))

        defaults = set()
        for df in root.findall(f"{{{ns}}}Default"):
            defaults.add("." + df.get("Extension", ""))

        # Check for files without matching Override or Default
        for fpath in unpacked.rglob("*"):
            if fpath.is_dir() or fpath.name == "[Content_Types].xml":
                continue
            part_name = "/" + str(fpath.relative_to(unpacked)).replace(os.sep, "/")
            ext = fpath.suffix.lower()
            if part_name not in overrides and ext not in defaults:
                ct = _EXT_TYPES.get(ext)
                if ct:
                    if not dry_run:
                        new_elem = ET.SubElement(root, f"{{{ns}}}Default")
                        new_elem.set("Extension", ext.lstrip("."))
                        new_elem.set("ContentType", ct)
                        defaults.add(ext)
                    details.append(f"Added Default for extension '{ext}' → {ct}")

        if details and not dry_run:
            tree.write(ct_path, xml_declaration=True, encoding="UTF-8")
    except ET.ParseError:
        pass

    return details


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-repair OOXML structural issues")
    parser.add_argument("path", help="Unpacked OOXML directory")
    parser.add_argument("--dry-run", action="store_true", help="Report issues without modifying files")
    args = parser.parse_args()

    result = repair(args.path, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["repaired"] == 0 else 1)
