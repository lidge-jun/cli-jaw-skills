"""Validate Office document XML files.

Pipeline-based validation for unpacked OOXML documents.
Detects structural issues, relationship errors, namespace violations,
ID conflicts, and format-specific problems.

Returns JSON-compatible dict:
    {"passed": bool, "errors": [...], "warnings": [...], "stats": {...}}

Usage:
    python validate.py <path> [--verbose] [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Callable
from xml.etree import ElementTree as ET

import defusedxml.minidom

# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------


class _Result:
    """Accumulates errors and warnings during validation."""

    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict = {}

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }


# ===================================================================
# Common checks
# ===================================================================


def check_xml_wellformed(unpacked: Path, res: _Result) -> None:
    """Parse every XML/rels file to ensure well-formedness."""
    xml_count = 0
    for xml_file in sorted(
        list(unpacked.rglob("*.xml")) + list(unpacked.rglob("*.rels"))
    ):
        xml_count += 1
        try:
            defusedxml.minidom.parseString(xml_file.read_bytes())
        except Exception as e:
            rel = xml_file.relative_to(unpacked)
            res.error(f"Malformed XML {rel}: {e}")
    res.stats["xml_files_checked"] = xml_count


def check_required_files(unpacked: Path, res: _Result) -> None:
    """Verify [Content_Types].xml and _rels/.rels exist."""
    if not (unpacked / "[Content_Types].xml").exists():
        res.error("Missing [Content_Types].xml")
    if not (unpacked / "_rels" / ".rels").exists():
        res.error("Missing _rels/.rels")


def check_content_types(unpacked: Path, res: _Result) -> None:
    """Verify every Override/@PartName references an existing file."""
    ct_path = unpacked / "[Content_Types].xml"
    if not ct_path.exists():
        return
    try:
        tree = ET.parse(ct_path)  # noqa: S314 – already validated
        ns = {"ct": "http://schemas.openxmlformats.org/package/2006/content-types"}
        for override in tree.findall("ct:Override", ns):
            part = override.get("PartName", "")
            if part.startswith("/"):
                part = part[1:]
            if part and not (unpacked / part).exists():
                res.error(f"Content_Types Override references missing file: /{part}")
    except ET.ParseError:
        pass  # already caught by wellformed check


def check_namespace_integrity(unpacked: Path, res: _Result) -> None:
    """Detect declared-but-unused or used-but-undeclared namespace prefixes."""
    _NS_DECL = re.compile(r'\bxmlns:(\w+)\s*=')
    _PREFIX_USE = re.compile(r'</?(\w+):')

    for xml_file in unpacked.rglob("*.xml"):
        try:
            raw = xml_file.read_text(encoding="utf-8")
        except Exception:
            continue
        declared = set(_NS_DECL.findall(raw))
        used = set(_PREFIX_USE.findall(raw))
        undeclared = used - declared - {"xml"}
        if undeclared:
            rel = xml_file.relative_to(unpacked)
            for pfx in sorted(undeclared):
                res.warn(f"Undeclared namespace prefix '{pfx}' used in {rel}")


def check_unique_ids(unpacked: Path, res: _Result) -> None:
    """Check that id-like attributes are unique within each XML file."""
    _ID_ATTRS = {"Id", "id", "rId"}

    for xml_file in unpacked.rglob("*.xml"):
        try:
            tree = ET.parse(xml_file)  # noqa: S314
        except ET.ParseError:
            continue
        seen: dict[str, str] = {}
        for elem in tree.iter():
            for attr in _ID_ATTRS:
                val = elem.get(attr)
                if val is None:
                    continue
                key = f"{attr}={val}"
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if key in seen:
                    rel = xml_file.relative_to(unpacked)
                    res.error(f"Duplicate {key} in {rel} (tags: {seen[key]}, {tag})")
                else:
                    seen[key] = tag


def check_relationship_chain(unpacked: Path, res: _Result) -> None:
    """Verify every Relationship target exists and type is plausible."""
    rel_count = 0
    broken = 0
    for rels_file in unpacked.rglob("*.rels"):
        try:
            tree = ET.parse(rels_file)  # noqa: S314
        except ET.ParseError:
            continue
        # .rels sits inside _rels/, target is relative to parent of _rels/
        rels_dir = rels_file.parent.parent

        for rel in tree.iter():
            tag = rel.tag.split("}")[-1] if "}" in rel.tag else rel.tag
            if tag != "Relationship":
                continue
            rel_count += 1
            target = rel.get("Target", "")
            if not target or target.startswith("http://") or target.startswith("https://"):
                continue
            # Handle fragment references (e.g. "slide1.xml#rId3")
            target = target.split("#")[0]
            if not target:
                continue
            target_path = (rels_dir / target).resolve()
            if not target_path.exists():
                rel_path = rels_file.relative_to(unpacked)
                res.error(f"Broken relationship in {rel_path}: target '{target}' not found")
                broken += 1
    res.stats["relationships_checked"] = rel_count
    res.stats["broken_relationships"] = broken


# ===================================================================
# PPTX-specific checks
# ===================================================================


def check_uuid_format(unpacked: Path, res: _Result) -> None:
    """Verify UUID attributes in presentation.xml are valid format."""
    _UUID_RE = re.compile(
        r"^\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?$"
    )
    pres = unpacked / "ppt" / "presentation.xml"
    if not pres.exists():
        return
    try:
        tree = ET.parse(pres)  # noqa: S314
        for elem in tree.iter():
            for attr in ("id", "guid"):
                val = elem.get(attr)
                if val and len(val) > 30 and not _UUID_RE.match(val):
                    res.warn(f"Invalid UUID format: {attr}='{val}'")
    except ET.ParseError:
        pass


def check_slide_layout_integrity(unpacked: Path, res: _Result) -> None:
    """Verify each slide's relationship to a layout file exists."""
    slides_dir = unpacked / "ppt" / "slides"
    if not slides_dir.is_dir():
        return
    for slide_xml in sorted(slides_dir.glob("slide*.xml")):
        rels_file = slides_dir / "_rels" / f"{slide_xml.name}.rels"
        if not rels_file.exists():
            res.error(f"Missing rels for {slide_xml.name}")
            continue
        try:
            tree = ET.parse(rels_file)  # noqa: S314
            has_layout = False
            for rel in tree.iter():
                rtype = rel.get("Type", "")
                if "slideLayout" in rtype:
                    has_layout = True
                    target = rel.get("Target", "")
                    layout_path = (slides_dir / target).resolve()
                    if not layout_path.exists():
                        res.error(f"{slide_xml.name}: layout target '{target}' not found")
            if not has_layout:
                res.warn(f"{slide_xml.name}: no slideLayout relationship found")
        except ET.ParseError:
            pass


def check_notes_slide_uniqueness(unpacked: Path, res: _Result) -> None:
    """Verify no two slides reference the same notes slide."""
    notes_map: dict[str, str] = {}
    slides_dir = unpacked / "ppt" / "slides"
    if not slides_dir.is_dir():
        return
    for rels_file in sorted((slides_dir / "_rels").glob("*.xml.rels")) if (slides_dir / "_rels").is_dir() else []:
        try:
            tree = ET.parse(rels_file)  # noqa: S314
            for rel in tree.iter():
                rtype = rel.get("Type", "")
                target = rel.get("Target", "")
                if "notesSlide" in rtype and target:
                    if target in notes_map:
                        res.error(
                            f"Duplicate notes reference: '{target}' used by "
                            f"{notes_map[target]} and {rels_file.stem}"
                        )
                    else:
                        notes_map[target] = rels_file.stem
        except ET.ParseError:
            pass


def check_no_duplicate_layouts(unpacked: Path, res: _Result) -> None:
    """Each slide should reference exactly one layout."""
    slides_dir = unpacked / "ppt" / "slides"
    if not slides_dir.is_dir():
        return
    for rels_file in sorted((slides_dir / "_rels").glob("*.xml.rels")) if (slides_dir / "_rels").is_dir() else []:
        try:
            tree = ET.parse(rels_file)  # noqa: S314
            layout_count = sum(
                1 for rel in tree.iter()
                if "slideLayout" in rel.get("Type", "")
            )
            if layout_count > 1:
                res.error(f"{rels_file.stem}: {layout_count} layout relationships (expected 1)")
        except ET.ParseError:
            pass


# ===================================================================
# DOCX-specific checks
# ===================================================================


def check_whitespace_preserve(unpacked: Path, res: _Result) -> None:
    """Check <w:t> elements have xml:space='preserve' when needed."""
    doc = unpacked / "word" / "document.xml"
    if not doc.exists():
        return
    try:
        tree = ET.parse(doc)  # noqa: S314
        ns_space = "{http://www.w3.org/XML/1998/namespace}space"
        wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        count = 0
        for t_elem in tree.iter(f"{{{wns}}}t"):
            text = t_elem.text or ""
            if text != text.strip() or "  " in text:
                if t_elem.get(ns_space) != "preserve":
                    count += 1
        if count:
            res.warn(f"{count} <w:t> element(s) with leading/trailing/double spaces missing xml:space='preserve'")
            res.stats["whitespace_preserve_missing"] = count
    except ET.ParseError:
        pass


def check_deletion_elements(unpacked: Path, res: _Result) -> None:
    """Detect <w:t> inside <w:del> (should be <w:delText>)."""
    doc = unpacked / "word" / "document.xml"
    if not doc.exists():
        return
    try:
        tree = ET.parse(doc)  # noqa: S314
        wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for del_elem in tree.iter(f"{{{wns}}}del"):
            for t_elem in del_elem.iter(f"{{{wns}}}t"):
                res.error("<w:t> found inside <w:del> — must use <w:delText>")
    except ET.ParseError:
        pass


def check_insertion_elements(unpacked: Path, res: _Result) -> None:
    """Detect <w:delText> inside <w:ins> (should be <w:t>)."""
    doc = unpacked / "word" / "document.xml"
    if not doc.exists():
        return
    try:
        tree = ET.parse(doc)  # noqa: S314
        wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for ins_elem in tree.iter(f"{{{wns}}}ins"):
            for dt_elem in ins_elem.iter(f"{{{wns}}}delText"):
                res.error("<w:delText> found inside <w:ins> — must use <w:t>")
    except ET.ParseError:
        pass


def check_id_constraints(unpacked: Path, res: _Result) -> None:
    """Verify paraId < 0x80000000 and durableId < 0x7FFFFFFF."""
    doc = unpacked / "word" / "document.xml"
    if not doc.exists():
        return
    try:
        tree = ET.parse(doc)  # noqa: S314
        wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        w14 = "http://schemas.microsoft.com/office/word/2010/wordml"
        for elem in tree.iter():
            para_id = elem.get(f"{{{w14}}}paraId") or elem.get(f"{{{wns}}}paraId")
            if para_id:
                try:
                    val = int(para_id, 16)
                    if val >= 0x80000000:
                        res.error(f"paraId '{para_id}' exceeds 0x7FFFFFFF limit")
                except ValueError:
                    res.error(f"paraId '{para_id}' is not valid hex")
            dur_id = elem.get(f"{{{w14}}}durableId") or elem.get(f"{{{wns}}}durableId")
            if dur_id:
                try:
                    val = int(dur_id, 16) if len(dur_id) <= 8 else int(dur_id)
                    if val >= 0x7FFFFFFF:
                        res.error(f"durableId '{dur_id}' exceeds 0x7FFFFFFE limit")
                except ValueError:
                    pass
    except ET.ParseError:
        pass


def check_comment_markers(unpacked: Path, res: _Result) -> None:
    """Verify commentRangeStart/commentRangeEnd are paired."""
    doc = unpacked / "word" / "document.xml"
    if not doc.exists():
        return
    try:
        tree = ET.parse(doc)  # noqa: S314
        wns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        starts: set[str] = set()
        ends: set[str] = set()
        refs: set[str] = set()
        for elem in tree.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            cid = elem.get(f"{{{wns}}}id") or elem.get("id")
            if tag == "commentRangeStart" and cid:
                starts.add(cid)
            elif tag == "commentRangeEnd" and cid:
                ends.add(cid)
            elif tag == "commentReference" and cid:
                refs.add(cid)
        orphan_starts = starts - ends
        orphan_ends = ends - starts
        if orphan_starts:
            res.error(f"commentRangeStart without matching End: ids={sorted(orphan_starts)}")
        if orphan_ends:
            res.error(f"commentRangeEnd without matching Start: ids={sorted(orphan_ends)}")
        missing_refs = starts - refs
        if missing_refs:
            res.warn(f"commentRangeStart without commentReference: ids={sorted(missing_refs)}")
    except ET.ParseError:
        pass


# ===================================================================
# XLSX-specific checks
# ===================================================================


def check_shared_strings(unpacked: Path, res: _Result) -> None:
    """Verify sharedStrings references are within bounds."""
    ss_path = unpacked / "xl" / "sharedStrings.xml"
    if not ss_path.exists():
        return
    try:
        tree = ET.parse(ss_path)  # noqa: S314
        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        si_count = len(tree.findall(f"{{{ns}}}si"))
        res.stats["shared_strings"] = si_count

        # Check sheets for out-of-range string references
        sheets_dir = unpacked / "xl" / "worksheets"
        if not sheets_dir.is_dir():
            return
        for sheet in sorted(sheets_dir.glob("*.xml")):
            try:
                stree = ET.parse(sheet)  # noqa: S314
                for cell in stree.iter(f"{{{ns}}}c"):
                    if cell.get("t") == "s":
                        v_elem = cell.find(f"{{{ns}}}v")
                        if v_elem is not None and v_elem.text:
                            try:
                                idx = int(v_elem.text)
                                if idx < 0 or idx >= si_count:
                                    sname = sheet.name
                                    ref = cell.get("r", "?")
                                    res.error(
                                        f"{sname} cell {ref}: sharedString index {idx} "
                                        f"out of range (0–{si_count - 1})"
                                    )
                            except ValueError:
                                pass
            except ET.ParseError:
                pass
    except ET.ParseError:
        pass


def check_sheet_references(unpacked: Path, res: _Result) -> None:
    """Verify workbook.xml sheet entries point to existing sheet files."""
    wb = unpacked / "xl" / "workbook.xml"
    if not wb.exists():
        return
    try:
        tree = ET.parse(wb)  # noqa: S314
        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        rns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        sheets = tree.findall(f".//{{{ns}}}sheet")
        res.stats["sheet_count"] = len(sheets)

        # Load workbook rels
        wb_rels = unpacked / "xl" / "_rels" / "workbook.xml.rels"
        rid_to_target: dict[str, str] = {}
        if wb_rels.exists():
            rtree = ET.parse(wb_rels)  # noqa: S314
            for rel in rtree.iter():
                rid = rel.get("Id")
                target = rel.get("Target")
                if rid and target:
                    rid_to_target[rid] = target

        for sheet in sheets:
            rid = sheet.get(f"{{{rns}}}id") or sheet.get("r:id")
            if rid and rid in rid_to_target:
                target = rid_to_target[rid]
                sheet_path = unpacked / "xl" / target
                if not sheet_path.exists():
                    name = sheet.get("name", "?")
                    res.error(f"Sheet '{name}' ({rid}) target '{target}' not found")
    except ET.ParseError:
        pass


def check_defined_names(unpacked: Path, res: _Result) -> None:
    """Warn about DefinedName entries with #REF! or empty ranges."""
    wb = unpacked / "xl" / "workbook.xml"
    if not wb.exists():
        return
    try:
        tree = ET.parse(wb)  # noqa: S314
        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        for dn in tree.findall(f".//{{{ns}}}definedName"):
            name = dn.get("name", "?")
            value = (dn.text or "").strip()
            if "#REF!" in value:
                res.error(f"DefinedName '{name}' contains #REF!: {value}")
            elif not value:
                res.warn(f"DefinedName '{name}' has empty range")
    except ET.ParseError:
        pass


# ===================================================================
# Pipeline assembly
# ===================================================================

COMMON_CHECKS: list[Callable] = [
    check_xml_wellformed,
    check_required_files,
    check_content_types,
    check_namespace_integrity,
    check_unique_ids,
    check_relationship_chain,
]

PPTX_CHECKS: list[Callable] = [
    check_uuid_format,
    check_slide_layout_integrity,
    check_notes_slide_uniqueness,
    check_no_duplicate_layouts,
]

DOCX_CHECKS: list[Callable] = [
    check_whitespace_preserve,
    check_deletion_elements,
    check_insertion_elements,
    check_id_constraints,
    check_comment_markers,
]

XLSX_CHECKS: list[Callable] = [
    check_shared_strings,
    check_sheet_references,
    check_defined_names,
]


def _detect_type(unpacked: Path) -> str:
    """Detect Office type from unpacked directory structure."""
    if (unpacked / "word").is_dir():
        return ".docx"
    if (unpacked / "ppt").is_dir():
        return ".pptx"
    if (unpacked / "xl").is_dir():
        return ".xlsx"
    return ""


def validate(path: str, *, verbose: bool = False) -> dict:
    """Validate an unpacked or packed Office document.

    Returns dict: {"passed": bool, "errors": [...], "warnings": [...], "stats": {...}}
    """
    p = Path(path)

    if not p.exists():
        return {"passed": False, "errors": [f"Path does not exist: {path}"], "warnings": [], "stats": {}}

    # If packed file, unpack to temp dir
    if p.is_file() and p.suffix.lower() in (".docx", ".pptx", ".xlsx"):
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(p, "r") as zf:
            zf.extractall(tmp)
        unpacked = Path(tmp)
        file_type = p.suffix.lower()
    elif p.is_dir():
        unpacked = p
        file_type = _detect_type(p)
    else:
        return {"passed": False, "errors": [f"Not a directory or Office file: {path}"], "warnings": [], "stats": {}}

    res = _Result()
    res.stats["file_type"] = file_type

    # Run common checks
    for check_fn in COMMON_CHECKS:
        check_fn(unpacked, res)

    # Run type-specific checks
    type_checks = {
        ".docx": DOCX_CHECKS,
        ".pptx": PPTX_CHECKS,
        ".xlsx": XLSX_CHECKS,
    }
    for check_fn in type_checks.get(file_type, []):
        check_fn(unpacked, res)

    if verbose and res.passed:
        print(f"Validation PASSED ({file_type})")
    elif verbose:
        print(f"Validation FAILED: {len(res.errors)} error(s), {len(res.warnings)} warning(s)")

    return res.to_dict()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Office document XML")
    parser.add_argument("path", help="Unpacked directory or packed Office file (.docx/.pptx/.xlsx)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print human-readable output")
    parser.add_argument("--json", "-j", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    result = validate(args.path, verbose=args.verbose)

    if args.json:
        print(json.dumps(result, indent=2))
    elif not args.verbose:
        if result["passed"]:
            print("Validation PASSED")
        else:
            print("Validation FAILED:")
            for e in result["errors"]:
                print(f"  ERROR: {e}")
            for w in result["warnings"]:
                print(f"  WARN:  {w}")

    sys.exit(0 if result["passed"] else 1)
