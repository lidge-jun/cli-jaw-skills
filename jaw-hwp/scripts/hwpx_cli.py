#!/usr/bin/env python3
"""Unified CLI for HWPX document operations.

Subcommands:
    open        Unpack HWPX to directory with pretty-printed XML
    save        Pack directory to HWPX (atomic write, auto strip+minify)
    text        Extract text from HWPX
    search      Search text content with regex
    replace     Replace text in HWPX
    batch-replace  Bulk replace from JSON map
    tables      List tables or export as CSV
    fill-table  Fill table cells by label-path (e.g. "이름 > 오른쪽")
    validate    Structural validation
    page-guard  Page drift detection against reference
    structure   Document structure tree

Usage:
    python hwpx_cli.py open input.hwpx work/
    python hwpx_cli.py save work/ output.hwpx
    python hwpx_cli.py text input.hwpx
    python hwpx_cli.py search input.hwpx "pattern"
    python hwpx_cli.py replace input.hwpx "old" "new" -o out.hwpx
    python hwpx_cli.py batch-replace input.hwpx map.json -o out.hwpx
    python hwpx_cli.py tables input.hwpx --csv
    python hwpx_cli.py fill-table input.hwpx 0 '{"이름 > right": "홍길동"}' -o out.hwpx
    python hwpx_cli.py validate input.hwpx
    python hwpx_cli.py page-guard -r ref.hwpx -o out.hwpx
    python hwpx_cli.py structure input.hwpx
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent

NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_section_xml(hwpx_path: str, section: int = 0) -> etree._Element:
    """Read and parse a section XML from HWPX ZIP."""
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        data = zf.read(f"Contents/section{section}.xml")
    return etree.fromstring(data)


def _get_all_text_nodes(root: etree._Element) -> list[etree._Element]:
    """Get all hp:t nodes."""
    return root.xpath(".//hp:t", namespaces=NS)


def _get_text(el: etree._Element) -> str:
    """Get concatenated text from an element's hp:t descendants."""
    parts = []
    for t in el.findall(".//hp:t", NS):
        if t.text:
            parts.append(t.text)
    return "".join(parts)


def _unpack_to_tmpdir(hwpx_path: str) -> str:
    """Unpack HWPX to a temp directory, return path."""
    tmpdir = tempfile.mkdtemp(prefix="hwpx_cli_")
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        zf.extractall(tmpdir)
    return tmpdir


def _repack_atomic(work_dir: str, output_path: str) -> None:
    """Repack using pack.py with atomic save."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from office.pack import pack
    pack(work_dir, output_path, strip_lsa=True, minify=True)


def _section_files(hwpx_path: str) -> list[str]:
    """List section XML filenames inside HWPX."""
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return sorted(
            n for n in zf.namelist()
            if n.startswith("Contents/section") and n.endswith(".xml")
        )


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_open(args: argparse.Namespace) -> int:
    """Unpack HWPX with pretty-printed XML."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from office.unpack import unpack
    unpack(args.input, args.output_dir)
    return 0


def cmd_save(args: argparse.Namespace) -> int:
    """Pack directory to HWPX (atomic, strip+minify)."""
    _repack_atomic(args.input_dir, args.output)
    return 0


def cmd_text(args: argparse.Namespace) -> int:
    """Extract text from HWPX."""
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))
        for t_node in _get_all_text_nodes(root):
            if t_node.text and t_node.text.strip():
                print(t_node.text)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search text content with regex."""
    pattern = re.compile(args.pattern)
    results: list[dict] = []
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))
        paragraphs = root.xpath(".//hp:p", namespaces=NS)
        for i, p in enumerate(paragraphs):
            text = _get_text(p)
            if pattern.search(text):
                results.append({"section": sec_name, "para_index": i, "text": text[:120]})
    if not results:
        print("No matches found.", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['section']}:p{r['para_index']}: {r['text']}")
    print(f"\n{len(results)} match(es) found.", file=sys.stderr)
    return 0


def cmd_replace(args: argparse.Namespace) -> int:
    """Replace text in HWPX."""
    work = _unpack_to_tmpdir(args.input)
    try:
        replaced = 0
        for xml_path in Path(work).rglob("section*.xml"):
            content = xml_path.read_text(encoding="utf-8")
            new_content, n = re.subn(re.escape(args.old), args.new, content)
            if n > 0:
                xml_path.write_text(new_content, encoding="utf-8")
                replaced += n

        if replaced == 0:
            print(f"No occurrences of '{args.old}' found.", file=sys.stderr)
            return 1

        output = args.output or args.input
        _repack_atomic(work, output)
        print(f"Replaced {replaced} occurrence(s). Output: {output}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_batch_replace(args: argparse.Namespace) -> int:
    """Bulk replace from JSON map file."""
    with open(args.map_file, "r", encoding="utf-8") as f:
        replacements: dict[str, str] = json.load(f)

    work = _unpack_to_tmpdir(args.input)
    try:
        total = 0
        for xml_path in Path(work).rglob("section*.xml"):
            content = xml_path.read_text(encoding="utf-8")
            for old, new in replacements.items():
                content, n = re.subn(re.escape(old), new, content)
                total += n
            xml_path.write_text(content, encoding="utf-8")

        if total == 0:
            print("No replacements made.", file=sys.stderr)
            return 1

        output = args.output or args.input
        _repack_atomic(work, output)
        print(f"Replaced {total} total occurrence(s). Output: {output}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_tables(args: argparse.Namespace) -> int:
    """List tables or export as CSV/JSON."""
    all_tables: list[dict] = []
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))

        tables = root.xpath(".//hp:tbl", namespaces=NS)
        for idx, tbl in enumerate(tables):
            rows = int(tbl.get("rowCnt", "0"))
            cols = int(tbl.get("colCnt", "0"))
            cells: list[list[str]] = []
            for tr in tbl.findall("hp:tr", NS):
                row_data = []
                for tc in tr.findall("hp:tc", NS):
                    row_data.append(_get_text(tc))
                cells.append(row_data)
            all_tables.append({"index": idx, "rows": rows, "cols": cols, "cells": cells})

    if args.json:
        print(json.dumps(all_tables, ensure_ascii=False, indent=2))
    elif args.csv:
        for t in all_tables:
            print(f"Table {t['index']}: {t['rows']}×{t['cols']}")
            writer = csv.writer(sys.stdout)
            for row in t["cells"]:
                writer.writerow(row)
            print()
    else:
        for t in all_tables:
            print(f"Table {t['index']}: {t['rows']}×{t['cols']}")
    return 0


def cmd_fill_table(args: argparse.Namespace) -> int:
    """Fill table cells by label-path navigation.

    Path format: "label > direction" where direction is:
      right, left, below, above (or Korean: 오른쪽, 왼쪽, 아래, 위)

    Example: {"이름 > right": "홍길동", "전화번호 > right": "010-1234-5678"}
    """
    fill_map: dict[str, str] = json.loads(args.fill_json)

    work = _unpack_to_tmpdir(args.input)
    try:
        filled = 0
        for xml_path in sorted(Path(work).glob("Contents/section*.xml")):
            tree = etree.parse(str(xml_path))
            root = tree.getroot()
            tables = root.xpath(".//hp:tbl", namespaces=NS)

            if args.table_index >= len(tables):
                continue

            tbl = tables[args.table_index]

            # Build cell grid: (row, col) -> tc element
            grid: dict[tuple[int, int], etree._Element] = {}
            for tr in tbl.findall("hp:tr", NS):
                for tc in tr.findall("hp:tc", NS):
                    addr = tc.find("hp:cellAddr", NS)
                    if addr is not None:
                        r = int(addr.get("rowAddr", "0"))
                        c = int(addr.get("colAddr", "0"))
                        grid[(r, c)] = tc

            # For each fill spec, find label cell, navigate, fill
            for path_spec, value in fill_map.items():
                parts = [p.strip() for p in path_spec.split(">")]
                if len(parts) != 2:
                    print(f"Invalid path spec (need 'label > direction'): {path_spec}", file=sys.stderr)
                    continue

                label, direction = parts[0], parts[1].lower()

                # Direction aliases
                dir_map = {
                    "right": (0, 1), "오른쪽": (0, 1),
                    "left": (0, -1), "왼쪽": (0, -1),
                    "below": (1, 0), "아래": (1, 0),
                    "above": (-1, 0), "위": (-1, 0),
                }
                if direction not in dir_map:
                    print(f"Unknown direction '{direction}'. Use: right/left/below/above", file=sys.stderr)
                    continue

                dr, dc = dir_map[direction]

                # Find cell containing label text
                target_rc = None
                for (r, c), tc in grid.items():
                    if label in _get_text(tc):
                        target_rc = (r + dr, c + dc)
                        break

                if target_rc is None:
                    print(f"Label '{label}' not found in table {args.table_index}", file=sys.stderr)
                    continue

                target_tc = grid.get(target_rc)
                if target_tc is None:
                    print(f"Target cell {target_rc} does not exist for '{path_spec}'", file=sys.stderr)
                    continue

                # Set cell text: find first hp:t or create one
                t_nodes = target_tc.xpath(".//hp:t", namespaces=NS)
                if t_nodes:
                    t_nodes[0].text = value
                    # Clear any extra t nodes
                    for extra in t_nodes[1:]:
                        extra.text = ""
                else:
                    # Create minimal paragraph structure
                    sub = target_tc.find("hp:subList", NS)
                    if sub is None:
                        sub = target_tc.find(".//hp:p", NS)
                    if sub is not None:
                        runs = sub.findall(".//hp:run", NS)
                        if runs:
                            t_el = runs[0].find("hp:t", NS)
                            if t_el is not None:
                                t_el.text = value
                            else:
                                t_el = etree.SubElement(runs[0], f"{{{NS['hp']}}}t")
                                t_el.text = value

                filled += 1
                print(f"  Filled: {path_spec} = {value}")

            # Write back
            tree.write(str(xml_path), xml_declaration=True, encoding="UTF-8")

        if filled == 0:
            print("No cells were filled.", file=sys.stderr)
            return 1

        output = args.output or args.input
        _repack_atomic(work, output)
        print(f"Filled {filled} cell(s). Output: {output}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_validate(args: argparse.Namespace) -> int:
    """Structural validation."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from validate import validate
    errors = validate(args.input)
    if args.json:
        result = {"status": "INVALID" if errors else "VALID", "file": args.input, "errors": errors}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print(f"INVALID: {args.input}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
    else:
        print(f"VALID: {args.input}")
    return 1 if errors else 0


def cmd_page_guard(args: argparse.Namespace) -> int:
    """Page drift detection."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from page_guard import collect_metrics, compare_metrics
    from dataclasses import asdict
    ref = collect_metrics(Path(args.reference))
    out = collect_metrics(Path(args.output))
    errors = compare_metrics(ref, out, args.max_text_delta, args.max_para_delta)
    if args.json:
        result = {
            "status": "FAIL" if errors else "PASS",
            "reference": args.reference,
            "output": args.output,
            "errors": errors,
            "metrics": {"reference": asdict(ref), "output": asdict(out)},
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif errors:
        print("FAIL: page-guard")
        for e in errors:
            print(f"  - {e}")
    else:
        print("PASS: page-guard")
    return 1 if errors else 0


# ---------------------------------------------------------------------------
# Agentic Reading + repair_xml (plan3)
# ---------------------------------------------------------------------------

def _read_header_xml(hwpx_path: str) -> etree._Element:
    """Read and parse header.xml from HWPX ZIP."""
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return etree.fromstring(zf.read("Contents/header.xml"))


def _get_heading_para_ids(header_root: etree._Element) -> dict[str, int]:
    """Return {paraPr_id: heading_level} for paraPr with explicit OUTLINE heading."""
    heading_map: dict[str, int] = {}
    for pp in header_root.findall(".//hh:paraPr", NS):
        heading = pp.find("hh:heading", NS)
        if heading is not None and heading.get("type", "NONE") != "NONE":
            pid = pp.get("id")
            if pid is not None:
                heading_map[pid] = int(heading.get("level", "0"))
    return heading_map


def _build_toc(hwpx_path: str) -> list[dict]:
    """Build table of contents from heading paragraphs."""
    header_root = _read_header_xml(hwpx_path)
    heading_ids = _get_heading_para_ids(header_root)

    if not heading_ids:
        return []

    toc: list[dict] = []
    for sec_name in _section_files(hwpx_path):
        with zipfile.ZipFile(hwpx_path, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))

        all_paras = root.xpath(".//hp:p", namespaces=NS)
        for i, p in enumerate(all_paras):
            ppr_id = p.get("paraPrIDRef", "0")
            if ppr_id in heading_ids:
                text = _get_text(p).strip()
                if text:
                    toc.append({
                        "level": heading_ids[ppr_id],
                        "title": text,
                        "para_index": i,
                        "section": sec_name,
                    })
    return toc


def _build_chunks(
    hwpx_path: str,
    by: str = "heading",
    max_chars: int = 4000,
) -> list[dict]:
    """Split document into chunks for agentic reading."""
    header_root = _read_header_xml(hwpx_path)
    heading_ids = _get_heading_para_ids(header_root)

    # If heading mode requested but no headings exist, fallback to size
    if by == "heading" and not heading_ids:
        by = "size"

    chunks: list[dict] = []
    chunk_id = 0

    for sec_name in _section_files(hwpx_path):
        with zipfile.ZipFile(hwpx_path, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))

        all_paras = root.xpath(".//hp:p", namespaces=NS)

        if by == "heading":
            current: dict = {"id": chunk_id, "title": "(intro)", "start_para": 0,
                             "paragraphs": [], "char_count": 0}

            for i, p in enumerate(all_paras):
                ppr_id = p.get("paraPrIDRef", "0")
                text = _get_text(p)

                if ppr_id in heading_ids and current["paragraphs"]:
                    current["end_para"] = i - 1
                    current["preview"] = _get_text(current["paragraphs"][0])[:80]
                    chunks.append(current)
                    chunk_id += 1
                    current = {"id": chunk_id, "title": text.strip(),
                               "start_para": i, "paragraphs": [], "char_count": 0}

                current["paragraphs"].append(p)
                current["char_count"] += len(text)

            if current["paragraphs"]:
                current["end_para"] = len(all_paras) - 1
                current["preview"] = _get_text(current["paragraphs"][0])[:80]
                chunks.append(current)
                chunk_id += 1

        elif by == "pagebreak":
            current = {"id": chunk_id, "title": f"page-{chunk_id}",
                        "start_para": 0, "paragraphs": [], "char_count": 0}

            for i, p in enumerate(all_paras):
                text = _get_text(p)
                if p.get("pageBreak") == "1" and current["paragraphs"]:
                    current["end_para"] = i - 1
                    current["preview"] = _get_text(current["paragraphs"][0])[:80]
                    chunks.append(current)
                    chunk_id += 1
                    current = {"id": chunk_id, "title": f"page-{chunk_id}",
                                "start_para": i, "paragraphs": [], "char_count": 0}

                current["paragraphs"].append(p)
                current["char_count"] += len(text)

            if current["paragraphs"]:
                current["end_para"] = len(all_paras) - 1
                current["preview"] = _get_text(current["paragraphs"][0])[:80]
                chunks.append(current)
                chunk_id += 1

        else:  # size
            current = {"id": chunk_id, "title": f"chunk-{chunk_id}",
                        "start_para": 0, "paragraphs": [], "char_count": 0}

            for i, p in enumerate(all_paras):
                text = _get_text(p)
                # Don't split inside a table — check if paragraph contains tbl
                has_table = p.find(".//hp:tbl", NS) is not None

                if current["char_count"] + len(text) > max_chars and current["paragraphs"] and not has_table:
                    current["end_para"] = i - 1
                    current["preview"] = _get_text(current["paragraphs"][0])[:80]
                    chunks.append(current)
                    chunk_id += 1
                    current = {"id": chunk_id, "title": f"chunk-{chunk_id}",
                                "start_para": i, "paragraphs": [], "char_count": 0}

                current["paragraphs"].append(p)
                current["char_count"] += len(text)

            if current["paragraphs"]:
                current["end_para"] = len(all_paras) - 1
                current["preview"] = _get_text(current["paragraphs"][0])[:80]
                chunks.append(current)
                chunk_id += 1

    # Strip non-serializable paragraph elements from output
    for c in chunks:
        del c["paragraphs"]

    return chunks


def cmd_toc(args: argparse.Namespace) -> int:
    """Extract table of contents from heading paragraphs."""
    toc = _build_toc(args.input)

    if not toc:
        print("No headings found. Use `chunk --by size` for documents without heading structure.",
              file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(toc, ensure_ascii=False, indent=2))
    else:
        for entry in toc:
            indent = "  " * entry["level"]
            print(f"{indent}{entry['title']} (p{entry['para_index']})")
    return 0


def cmd_chunk(args: argparse.Namespace) -> int:
    """Split document into chunks for agentic reading."""
    chunks = _build_chunks(args.input, by=args.by, max_chars=args.max_chars)

    if not chunks:
        print("No chunks produced.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(chunks, ensure_ascii=False, indent=2))
    else:
        for c in chunks:
            print(f"[{c['id']}] {c['title']} (p{c['start_para']}-p{c['end_para']}, {c['char_count']} chars)")
            if c.get("preview"):
                print(f"     {c['preview'][:60]}...")
    return 0


def cmd_search_chunks(args: argparse.Namespace) -> int:
    """Search within chunks for contextual results."""
    chunks_meta = _build_chunks(args.input, by="heading", max_chars=4000)
    pattern = re.compile(args.pattern)

    # Re-read paragraphs to match against chunks
    results: list[dict] = []
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))
        all_paras = root.xpath(".//hp:p", namespaces=NS)

        for chunk in chunks_meta:
            start = chunk["start_para"]
            end = chunk.get("end_para", len(all_paras) - 1)
            for pi in range(start, min(end + 1, len(all_paras))):
                text = _get_text(all_paras[pi])
                if pattern.search(text):
                    results.append({
                        "chunk_id": chunk["id"],
                        "chunk_title": chunk["title"],
                        "para_index": pi,
                        "context": text[:120],
                    })

    if not results:
        print("No matches found.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"[chunk {r['chunk_id']}] {r['chunk_title']} | p{r['para_index']}: {r['context']}")

    print(f"\n{len(results)} match(es) in {len(set(r['chunk_id'] for r in results))} chunk(s).",
          file=sys.stderr)
    return 0


def _collect_valid_ids(header_root: etree._Element) -> dict[str, set[str]]:
    """Collect valid IDs from header.xml for charPr, paraPr, borderFill."""
    ids: dict[str, set[str]] = {"charPr": set(), "paraPr": set(), "borderFill": set()}
    for cp in header_root.findall(".//hh:charPr", NS):
        cid = cp.get("id")
        if cid:
            ids["charPr"].add(cid)
    for pp in header_root.findall(".//hh:paraPr", NS):
        pid = pp.get("id")
        if pid:
            ids["paraPr"].add(pid)
    for bf in header_root.findall(".//hh:borderFill", NS):
        bid = bf.get("id")
        if bid:
            ids["borderFill"].add(bid)
    return ids


def _fix_xml_declaration(content: str) -> str:
    """Fix missing or duplicate XML declarations."""
    lines = content.split("\n")
    decl_indices = [i for i, l in enumerate(lines) if l.strip().startswith("<?xml")]

    if not decl_indices:
        # Missing — add standard declaration
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + content
    elif len(decl_indices) > 1:
        # Duplicate — keep first only
        for idx in reversed(decl_indices[1:]):
            lines.pop(idx)
        return "\n".join(lines)
    return content


def _reset_invalid_id_refs(root: etree._Element, valid_ids: dict[str, set[str]]) -> int:
    """Reset invalid IDRef attributes to 0. Returns count of resets."""
    resets = 0
    ref_map = {
        "charPrIDRef": "charPr",
        "paraPrIDRef": "paraPr",
        "borderFillIDRef": "borderFill",
    }

    for el in root.iter():
        for attr, id_type in ref_map.items():
            val = el.get(attr)
            if val is not None and val != "0" and val not in valid_ids.get(id_type, set()):
                el.set(attr, "0")
                resets += 1
    return resets


def cmd_repair(args: argparse.Namespace) -> int:
    """Diagnose and optionally repair HWPX XML issues.

    Default: dry-run (report only, no file changes).
    Use --apply or -o to actually fix safe issues.
    """
    apply = args.apply or args.output is not None

    work = _unpack_to_tmpdir(args.input)
    try:
        repairs: list[str] = []
        warnings: list[str] = []

        # Read header.xml for ID validation
        header_path = Path(work) / "Contents" / "header.xml"
        if header_path.is_file():
            header_root = etree.parse(str(header_path)).getroot()
            valid_ids = _collect_valid_ids(header_root)
        else:
            header_root = None
            valid_ids = {}

        # Only check section XMLs for IDRef (header.xml *defines* IDs, not references them)
        section_xml_names = {"section0.xml", "section1.xml", "section2.xml", "section3.xml"}

        sys.path.insert(0, str(SCRIPT_DIR))
        from office.pack import strip_linesegarray

        for xml_path in sorted(Path(work).rglob("*.xml")):
            content = xml_path.read_text(encoding="utf-8")
            original = content
            file_repairs: list[str] = []
            is_section = xml_path.name in section_xml_names

            # Safe auto-fix: XML declaration
            fixed = _fix_xml_declaration(content)
            if fixed != content:
                file_repairs.append("xml-declaration")
                content = fixed

            # Safe auto-fix: linesegarray strip (section XMLs only)
            if is_section:
                stripped = strip_linesegarray(content)
                if stripped != content:
                    file_repairs.append("linesegarray-stripped")
                    content = stripped

            # Try parsing — if fails, report but DON'T auto-fix
            try:
                root = etree.fromstring(content.encode("utf-8"))
                # Safe auto-fix: invalid IDRef → 0 (section XMLs only)
                if valid_ids and is_section:
                    n = _reset_invalid_id_refs(root, valid_ids)
                    if n > 0:
                        file_repairs.append(f"idref-reset({n})")
                        content = '<?xml version="1.0" encoding="UTF-8"?>' + etree.tostring(root, encoding="unicode")
            except etree.XMLSyntaxError as e:
                warnings.append(f"UNPARSEABLE: {xml_path.name}: {e}")

            if file_repairs:
                rel = xml_path.relative_to(work)
                repairs.append(f"{rel}: {', '.join(file_repairs)}")
                if apply:
                    xml_path.write_text(content, encoding="utf-8")

        # Output report
        if args.json:
            report = {
                "mode": "applied" if apply else "dry-run",
                "repairs": [{"file": r.split(":")[0].strip(), "actions": r.split(":")[1].strip()} for r in repairs] if repairs else [],
                "warnings": [{"file": w.split(":")[1].strip() if ":" in w else "", "message": w} for w in warnings] if warnings else [],
            }
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif repairs:
            label = "REPAIRED" if apply else "WOULD REPAIR"
            print(f"{label}:")
            for r in repairs:
                print(f"  - {r}")
            if warnings:
                print("WARNINGS (manual fix needed):")
                for w in warnings:
                    print(f"  - {w}")
        elif warnings:
            print("WARNINGS (manual fix needed):")
            for w in warnings:
                print(f"  - {w}")
        else:
            print("No issues found.")

        # Actually repack if applying
        if apply and repairs:
            output = args.output or args.input
            # Backup only when overwriting input (no -o specified)
            if not args.output:
                backup = Path(args.input).with_suffix(".hwpx.bak")
                if not backup.exists():
                    shutil.copy2(args.input, backup)
                    print(f"Backup: {backup}")
            _repack_atomic(work, output)
            print(f"Output: {output}")

            # Run validate
            sys.path.insert(0, str(SCRIPT_DIR))
            from validate import validate as validate_hwpx
            errors = validate_hwpx(output)
            if errors:
                print("WARNING: repaired file has validation issues:", file=sys.stderr)
                for e in errors:
                    print(f"  - {e}", file=sys.stderr)
            else:
                print("Post-repair validation: PASS")

        return 1 if warnings else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_content_check(args: argparse.Namespace) -> int:
    """Check content for required/forbidden keywords."""
    # 1. Extract all text
    full_text = ""
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))
        for t_node in _get_all_text_nodes(root):
            if t_node.text:
                full_text += t_node.text + "\n"

    results: dict = {"status": "PASS", "must_have": [], "must_not_have": []}

    # 2. must-have check
    if args.must_have:
        for kw in args.must_have.split(","):
            kw = kw.strip()
            if not kw:
                continue
            count = full_text.count(kw)
            entry: dict = {"keyword": kw, "found": count > 0, "count": count}
            if count > 0:
                idx = full_text.find(kw)
                entry["context"] = full_text[max(0, idx - 30):idx + len(kw) + 30].strip()
            else:
                results["status"] = "FAIL"
            results["must_have"].append(entry)

    # 3. must-not-have check
    if args.must_not_have:
        for kw in args.must_not_have.split(","):
            kw = kw.strip()
            if not kw:
                continue
            count = full_text.count(kw)
            entry = {"keyword": kw, "found": count > 0, "count": count}
            if count > 0:
                idx = full_text.find(kw)
                entry["context"] = full_text[max(0, idx - 30):idx + len(kw) + 30].strip()
                results["status"] = "FAIL"
            results["must_not_have"].append(entry)

    # 4. Output
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for item in results["must_have"]:
            mark = "✓" if item["found"] else "✗"
            print(f"  [MUST-HAVE] {mark} {item['keyword']} ({item['count']}건)")
        for item in results["must_not_have"]:
            mark = "✓ clean" if not item["found"] else f"✗ {item['count']}건"
            print(f"  [MUST-NOT]  {mark} {item['keyword']}")
            if item["found"] and "context" in item:
                print(f"              ...{item['context']}...")
        print(f"\nResult: {results['status']}", file=sys.stderr)

    return 0 if results["status"] == "PASS" else 1


def cmd_insert_table(args: argparse.Namespace) -> int:
    """Insert a table at a specific paragraph position."""
    import csv as csv_mod

    # 1. Parse data
    if args.table_json:
        data = json.loads(args.table_json)
    else:
        with open(args.csv, "r", encoding="utf-8") as f:
            data = list(csv_mod.reader(f))

    # 2. Build table XML via table_builder
    sys.path.insert(0, str(SCRIPT_DIR))
    from table_builder import build_table_paragraph_xml
    tbl_p_xml = build_table_paragraph_xml(data)
    tbl_p_el = etree.fromstring(tbl_p_xml)

    # 3. Unpack, insert into section0.xml, repack
    work = _unpack_to_tmpdir(args.input)
    try:
        sec_path = Path(work) / "Contents" / "section0.xml"
        tree = etree.parse(str(sec_path))
        root = tree.getroot()

        # Find top-level hp:p elements only (direct children, not nested in tables)
        top_paras = root.xpath("hp:p", namespaces=NS)

        if args.at_para is not None and args.at_para < len(top_paras):
            # Insert after the specified paragraph
            target = top_paras[args.at_para]
            idx = list(root).index(target)
            root.insert(idx + 1, tbl_p_el)
        else:
            # Append at end
            root.append(tbl_p_el)

        tree.write(str(sec_path), xml_declaration=True, encoding="utf-8")

        output = args.output or args.input
        _repack_atomic(work, output)
        print(f"Table inserted ({len(data)} rows x {len(data[0]) if data else 0} cols). Output: {output}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_structure(args: argparse.Namespace) -> int:
    """Document structure tree."""
    sys.path.insert(0, str(SCRIPT_DIR))
    # Delegate to analyze_template for full structure
    os.execvp(
        sys.executable,
        [sys.executable, str(SCRIPT_DIR / "analyze_template.py"), args.input],
    )
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified CLI for HWPX document operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # open
    p = sub.add_parser("open", help="Unpack HWPX to directory with pretty-printed XML")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("output_dir", help="Output directory")

    # save
    p = sub.add_parser("save", help="Pack directory to HWPX (atomic, strip+minify)")
    p.add_argument("input_dir", help="Input directory")
    p.add_argument("output", help="Output .hwpx file")

    # text
    p = sub.add_parser("text", help="Extract text from HWPX")
    p.add_argument("input", help="Input .hwpx file")

    # search
    p = sub.add_parser("search", help="Search text content with regex")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("pattern", help="Regex pattern to search")
    p.add_argument("--json", action="store_true", help="JSON output")

    # replace
    p = sub.add_parser("replace", help="Replace text in HWPX")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("old", help="Text to find")
    p.add_argument("new", help="Replacement text")
    p.add_argument("-o", "--output", help="Output file (default: overwrite input)")

    # batch-replace
    p = sub.add_parser("batch-replace", help="Bulk replace from JSON map")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("map_file", help="JSON file with {old: new} pairs")
    p.add_argument("-o", "--output", help="Output file (default: overwrite input)")

    # tables
    p = sub.add_parser("tables", help="List tables or export as CSV/JSON")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--csv", action="store_true", help="Export table contents as CSV")
    p.add_argument("--json", action="store_true", help="JSON output")

    # fill-table
    p = sub.add_parser("fill-table", help="Fill table cells by label-path")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("table_index", type=int, help="Table index (0-based)")
    p.add_argument("fill_json", help='JSON: {"label > direction": "value", ...}')
    p.add_argument("-o", "--output", help="Output file (default: overwrite input)")

    # validate
    p = sub.add_parser("validate", help="Structural validation")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--json", action="store_true", help="JSON output")

    # page-guard
    p = sub.add_parser("page-guard", help="Page drift detection against reference")
    p.add_argument("-r", "--reference", required=True, help="Reference .hwpx file")
    p.add_argument("-o", "--output", required=True, help="Output .hwpx file to check")
    p.add_argument("--max-text-delta", type=float, default=0.15)
    p.add_argument("--max-para-delta", type=float, default=0.25)
    p.add_argument("--json", action="store_true", help="JSON output")

    # toc
    p = sub.add_parser("toc", help="Extract table of contents from headings")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--json", action="store_true", help="JSON output")

    # chunk
    p = sub.add_parser("chunk", help="Split document into chunks for agentic reading")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--by", choices=["heading", "pagebreak", "size"], default="heading",
                   help="Chunking strategy (default: heading, falls back to size)")
    p.add_argument("--max-chars", type=int, default=4000,
                   help="Max chars per chunk for size mode (default: 4000)")
    p.add_argument("--json", action="store_true", help="JSON output")

    # search-chunks
    p = sub.add_parser("search-chunks", help="Search within document chunks")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("pattern", help="Search pattern (regex)")
    p.add_argument("--json", action="store_true", help="JSON output")

    # repair
    p = sub.add_parser("repair", help="Diagnose/repair HWPX XML issues (dry-run by default)")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--apply", action="store_true",
                   help="Actually apply safe repairs (default: dry-run report only)")
    p.add_argument("-o", "--output", help="Output file (implies --apply)")
    p.add_argument("--json", action="store_true", help="JSON output")

    # content-check
    p = sub.add_parser("content-check", help="Keyword-based content QA")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--must-have", help="Comma-separated keywords that MUST exist")
    p.add_argument("--must-not-have", help="Comma-separated keywords that must NOT exist")
    p.add_argument("--json", action="store_true", help="JSON output")

    # insert-table
    p = sub.add_parser("insert-table", help="Insert table at paragraph position")
    p.add_argument("input", help="Input .hwpx file")
    tbl_group = p.add_mutually_exclusive_group(required=True)
    tbl_group.add_argument("--json", metavar="JSON", dest="table_json",
                           help="JSON 2D array string")
    tbl_group.add_argument("--csv", metavar="FILE", help="CSV file")
    p.add_argument("--at-para", type=int,
                   help="Insert after paragraph N (0-based). Default: end")
    p.add_argument("-o", "--output", help="Output HWPX (default: overwrite input)")

    # structure
    p = sub.add_parser("structure", help="Document structure tree")
    p.add_argument("input", help="Input .hwpx file")

    args = parser.parse_args()

    commands = {
        "open": cmd_open,
        "save": cmd_save,
        "text": cmd_text,
        "search": cmd_search,
        "replace": cmd_replace,
        "batch-replace": cmd_batch_replace,
        "tables": cmd_tables,
        "fill-table": cmd_fill_table,
        "validate": cmd_validate,
        "page-guard": cmd_page_guard,
        "toc": cmd_toc,
        "chunk": cmd_chunk,
        "search-chunks": cmd_search_chunks,
        "repair": cmd_repair,
        "content-check": cmd_content_check,
        "insert-table": cmd_insert_table,
        "structure": cmd_structure,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
