#!/usr/bin/env python3
"""Regression test runner for docx_cli.py.

Compares actual CLI output against expected outputs in tests/expected/.

Usage:
    python run_tests.py                    # run all tests
    python run_tests.py --filter repair    # run only tests matching "repair"
    python run_tests.py --update           # update expected outputs from current results
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TESTS_DIR = SKILL_DIR / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
EXPECTED_DIR = TESTS_DIR / "expected"
CLI = SCRIPT_DIR / "docx_cli.py"

# (command, args, expected_file, compare_mode)
# compare_mode: "json" = parse+compare dicts, "text" = strip+compare strings
TEST_CASES: list[tuple[str, list[str], str, str]] = [
    # Validate
    ("validate", [str(FIXTURES_DIR / "broken_rels.docx"), "--json"],
     "validate_broken_rels.json", "json"),
    ("validate", [str(FIXTURES_DIR / "tracked_changes.docx"), "--json"],
     "validate_tracked_changes.json", "json"),
    ("validate", [str(FIXTURES_DIR / "tracked_changes_header_footer.docx"), "--json"],
     "validate_tracked_changes_header_footer.json", "json"),

    # Repair dry-run
    ("repair", [str(FIXTURES_DIR / "broken_rels.docx"), "--json"],
     "repair_broken_rels.json", "json"),

    # Text extraction
    ("text", [str(FIXTURES_DIR / "comments.docx")],
     "text_comments.txt", "text"),
    ("text", [str(FIXTURES_DIR / "tracked_changes.docx")],
     "text_tracked_changes.txt", "text"),

    # Agentic reading
    ("toc", [str(FIXTURES_DIR / "headings_report.docx"), "--json"],
     "toc_headings_report.json", "json"),
    ("chunk", [str(FIXTURES_DIR / "headings_report.docx"), "--json"],
     "chunk_headings_report.json", "json"),
    ("search-chunks", [str(FIXTURES_DIR / "headings_report.docx"), "market", "--json"],
     "search_chunks_headings_market.json", "json"),
]


def _load_expected(expected_file: str, mode: str):
    path = EXPECTED_DIR / expected_file
    raw = path.read_text(encoding="utf-8").strip()
    return json.loads(raw) if mode == "json" else raw


def _compare_expected(actual, expected_file: str, mode: str) -> tuple[bool, str]:
    expected = _load_expected(expected_file, mode)
    if mode == "json":
        return actual == expected, json.dumps(actual, ensure_ascii=False)
    return str(actual).strip() == str(expected).strip(), str(actual)


def run_accept_changes_regression() -> tuple[bool, str]:
    """Verify accept_changes removes revision tags from the fixture."""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "accepted.docx"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "accept_changes.py"),
                str(FIXTURES_DIR / "tracked_changes.docx"),
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False, result.stdout.strip() or result.stderr.strip()

        import defusedxml.minidom

        count = 0
        with zipfile.ZipFile(out_path, "r") as zf:
            for name in zf.namelist():
                if not name.startswith("word/") or not name.endswith(".xml"):
                    continue
                dom = defusedxml.minidom.parseString(zf.read(name))
                for tag in (
                    "ins", "del", "rPrChange", "pPrChange",
                    "tblPrChange", "trPrChange", "tcPrChange", "sectPrChange",
                ):
                    count += len(dom.getElementsByTagNameNS("*", tag))
        return count == 0, f"remaining revision tags={count}"


def run_accept_changes_header_footer_regression() -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "accepted_header_footer.docx"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "accept_changes.py"),
                str(FIXTURES_DIR / "tracked_changes_header_footer.docx"),
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False, result.stdout.strip() or result.stderr.strip()

        import defusedxml.minidom

        count = 0
        with zipfile.ZipFile(out_path, "r") as zf:
            for name in zf.namelist():
                if not name.startswith("word/") or not name.endswith(".xml"):
                    continue
                dom = defusedxml.minidom.parseString(zf.read(name))
                for tag in (
                    "ins", "del", "rPrChange", "pPrChange",
                    "tblPrChange", "trPrChange", "tcPrChange", "sectPrChange",
                ):
                    count += len(dom.getElementsByTagNameNS("*", tag))
        return _compare_expected(f"remaining revision tags={count}", "accept_changes_header_footer_zero.txt", "text")


def run_comment_exact_anchor_regression() -> tuple[bool, str]:
    """Verify exact anchor boundaries are isolated when anchors start/end mid-run."""
    import defusedxml.minidom
    from comment import _insert_comment_markers

    xml = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:t>xxHello</w:t></w:r>
      <w:r><w:t>Worldyy</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
    dom = defusedxml.minidom.parseString(xml)
    if not _insert_comment_markers(dom, 9, "HelloWorld"):
        return False, "anchor not inserted"

    para = dom.getElementsByTagNameNS(
        "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "p",
    )[0]
    nodes = [child for child in para.childNodes if getattr(child, "localName", None)]
    sequence = [node.localName for node in nodes]
    texts = []
    for node in nodes:
        if node.localName == "r":
            t_nodes = [
                child for child in node.childNodes
                if getattr(child, "localName", None) == "t"
            ]
            texts.append(t_nodes[0].childNodes[0].nodeValue if t_nodes and t_nodes[0].childNodes else "")
        else:
            texts.append("")

    expected_sequence = ["r", "commentRangeStart", "r", "r", "commentRangeEnd", "r", "r"]
    expected_texts = ["xx", "", "Hello", "World", "", "", "yy"]
    return (
        sequence == expected_sequence and texts == expected_texts,
        f"sequence={sequence} texts={texts}",
    )


def _comment_fixture_summary(fixture_name: str, anchor_text: str) -> tuple[bool, dict | str]:
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / f"commented-{fixture_name}"
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "comment.py"),
                str(FIXTURES_DIR / fixture_name),
                str(out_path),
                "--author",
                "Agent",
                "--text",
                "Fixture comment",
                "--anchor",
                anchor_text,
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return False, result.stdout.strip() or result.stderr.strip()

        import defusedxml.minidom

        with zipfile.ZipFile(out_path, "r") as zf:
            dom = defusedxml.minidom.parseString(zf.read("word/document.xml"))
        para = dom.getElementsByTagNameNS(
            "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
            "p",
        )[0]
        sequence = []
        texts = []
        for node in para.childNodes:
            local = getattr(node, "localName", None)
            if not local:
                continue
            sequence.append(local)
            if local == "r":
                t_nodes = [c for c in node.childNodes if getattr(c, "localName", None) == "t"]
                texts.append("".join(c.childNodes[0].nodeValue for c in t_nodes if c.childNodes))
            elif local == "hyperlink":
                inner = []
                for run in node.getElementsByTagNameNS(
                    "http://schemas.openxmlformats.org/wordprocessingml/2006/main", "r"
                ):
                    for child in run.childNodes:
                        if getattr(child, "localName", None) == "t" and child.childNodes:
                            inner.append(child.childNodes[0].nodeValue)
                texts.append("".join(inner))
            else:
                texts.append("")
        return True, {"sequence": sequence, "texts": texts}


def run_comment_mid_run_exact_regression() -> tuple[bool, str]:
    ok, payload = _comment_fixture_summary("comment_mid_run_exact.docx", "HelloWorld")
    if not ok:
        return False, str(payload)
    return _compare_expected(payload, "comment_mid_run_exact.json", "json")


def run_comment_multi_t_regression() -> tuple[bool, str]:
    ok, payload = _comment_fixture_summary("comment_multi_t_single_run.docx", "Hello")
    if not ok:
        return False, str(payload)
    return _compare_expected(payload, "comment_multi_t_single_run.json", "json")


def run_comment_hyperlink_boundary_regression() -> tuple[bool, str]:
    ok, payload = _comment_fixture_summary("comment_hyperlink_boundary.docx", "LinkTarget")
    if not ok:
        return False, str(payload)
    return _compare_expected(payload, "comment_hyperlink_boundary.json", "json")


def run_comment_field_code_boundary_regression() -> tuple[bool, str]:
    ok, payload = _comment_fixture_summary("comment_field_code_boundary.docx", "2026-03-27")
    if not ok:
        return False, str(payload)
    return _compare_expected(payload, "comment_field_code_boundary.json", "json")


UNIT_TESTS: list[tuple[str, callable]] = [
    ("accept-changes:tracked_changes_fixture", run_accept_changes_regression),
    ("accept-changes:header_footer_fixture", run_accept_changes_header_footer_regression),
    ("comment:exact_anchor_boundaries", run_comment_exact_anchor_regression),
    ("comment:mid_run_fixture", run_comment_mid_run_exact_regression),
    ("comment:multi_t_single_run_fixture", run_comment_multi_t_regression),
    ("comment:hyperlink_boundary_fixture", run_comment_hyperlink_boundary_regression),
    ("comment:field_code_boundary_fixture", run_comment_field_code_boundary_regression),
]


def run_cli(command: str, args: list[str], mode: str = "text") -> str:
    """Run docx_cli.py and capture output."""
    result = subprocess.run(
        [sys.executable, str(CLI), command] + args,
        capture_output=True,
        text=True,
    )
    if mode == "json":
        return result.stdout.strip()
    return (result.stdout + result.stderr).strip()


def compare(actual: str, expected: str, mode: str) -> bool:
    """Compare actual vs expected output."""
    if mode == "json":
        try:
            return json.loads(actual) == json.loads(expected)
        except json.JSONDecodeError:
            return False
    else:
        return actual.strip() == expected.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Regression test runner for docx_cli.py")
    parser.add_argument("--filter", help="Only run tests matching this string")
    parser.add_argument("--update", action="store_true", help="Update expected outputs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show diffs on failure")
    args = parser.parse_args()

    passed = 0
    failed = 0
    skipped = 0

    for command, cli_args, expected_file, mode in TEST_CASES:
        test_name = f"{command}:{expected_file}"

        if args.filter and args.filter not in test_name:
            skipped += 1
            continue

        expected_path = EXPECTED_DIR / expected_file

        actual = run_cli(command, cli_args, mode=mode)

        if args.update:
            expected_path.write_text(actual + "\n", encoding="utf-8")
            print(f"  UPDATED: {test_name}")
            passed += 1
            continue

        if not expected_path.is_file():
            print(f"  MISSING: {test_name} (no expected file)")
            failed += 1
            continue

        expected = expected_path.read_text(encoding="utf-8").strip()

        if compare(actual, expected, mode):
            print(f"  PASS: {test_name}")
            passed += 1
        else:
            print(f"  FAIL: {test_name}")
            if args.verbose:
                print(f"    Expected: {expected[:200]}")
                print(f"    Actual:   {actual[:200]}")
            failed += 1

    for test_name, test_fn in UNIT_TESTS:
        if args.filter and args.filter not in test_name:
            skipped += 1
            continue

        ok, detail = test_fn()
        if ok:
            print(f"  PASS: {test_name}")
            passed += 1
        else:
            print(f"  FAIL: {test_name}")
            if args.verbose:
                print(f"    Detail: {detail[:300]}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
