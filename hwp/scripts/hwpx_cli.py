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
    found = 0
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))
        paragraphs = root.xpath(".//hp:p", namespaces=NS)
        for i, p in enumerate(paragraphs):
            text = _get_text(p)
            if pattern.search(text):
                print(f"{sec_name}:p{i}: {text[:120]}")
                found += 1
    if found == 0:
        print("No matches found.", file=sys.stderr)
        return 1
    print(f"\n{found} match(es) found.", file=sys.stderr)
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
    """List tables or export as CSV."""
    for sec_name in _section_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = etree.fromstring(zf.read(sec_name))

        tables = root.xpath(".//hp:tbl", namespaces=NS)
        for idx, tbl in enumerate(tables):
            rows = int(tbl.get("rowCnt", "0"))
            cols = int(tbl.get("colCnt", "0"))
            print(f"Table {idx}: {rows}×{cols}")

            if args.csv:
                writer = csv.writer(sys.stdout)
                for tr in tbl.findall("hp:tr", NS):
                    row_data = []
                    for tc in tr.findall("hp:tc", NS):
                        row_data.append(_get_text(tc))
                    writer.writerow(row_data)
                print()
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
    if errors:
        print(f"INVALID: {args.input}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"VALID: {args.input}")
    return 0


def cmd_page_guard(args: argparse.Namespace) -> int:
    """Page drift detection."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from page_guard import collect_metrics, compare_metrics
    ref = collect_metrics(Path(args.reference))
    out = collect_metrics(Path(args.output))
    errors = compare_metrics(ref, out, args.max_text_delta, args.max_para_delta)
    if errors:
        print("FAIL: page-guard")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS: page-guard")
    return 0


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
    p = sub.add_parser("tables", help="List tables or export as CSV")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("--csv", action="store_true", help="Export table contents as CSV")

    # fill-table
    p = sub.add_parser("fill-table", help="Fill table cells by label-path")
    p.add_argument("input", help="Input .hwpx file")
    p.add_argument("table_index", type=int, help="Table index (0-based)")
    p.add_argument("fill_json", help='JSON: {"label > direction": "value", ...}')
    p.add_argument("-o", "--output", help="Output file (default: overwrite input)")

    # validate
    p = sub.add_parser("validate", help="Structural validation")
    p.add_argument("input", help="Input .hwpx file")

    # page-guard
    p = sub.add_parser("page-guard", help="Page drift detection against reference")
    p.add_argument("-r", "--reference", required=True, help="Reference .hwpx file")
    p.add_argument("-o", "--output", required=True, help="Output .hwpx file to check")
    p.add_argument("--max-text-delta", type=float, default=0.15)
    p.add_argument("--max-para-delta", type=float, default=0.25)

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
        "structure": cmd_structure,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
