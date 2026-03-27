#!/usr/bin/env python3
"""Regression test runner for pptx_cli.py.

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
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TESTS_DIR = SKILL_DIR / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
EXPECTED_DIR = TESTS_DIR / "expected"
CLI = SCRIPT_DIR / "pptx_cli.py"

# (command, args, expected_file, compare_mode)
TEST_CASES: list[tuple[str, list[str], str, str]] = [
    # Validate
    ("validate", [str(FIXTURES_DIR / "broken_layout.pptx"), "--json"],
     "validate_broken_layout.json", "json"),
    ("validate", [str(FIXTURES_DIR / "basic_slides.pptx"), "--json"],
     "validate_basic_slides.json", "json"),
    ("validate", [str(FIXTURES_DIR / "blankless_minimal_deck.pptx"), "--json"],
     "validate_blankless_minimal_deck.json", "json"),
    ("validate", [str(FIXTURES_DIR / "blank_layout_named_nonstandard.pptx"), "--json"],
     "validate_blank_layout_named_nonstandard.json", "json"),

    # Repair dry-run
    ("repair", [str(FIXTURES_DIR / "broken_layout.pptx"), "--json"],
     "repair_broken_layout.json", "json"),

    # Text extraction
    ("text", [str(FIXTURES_DIR / "basic_slides.pptx")],
     "text_basic_slides.txt", "text"),

    # Search
    ("search", [str(FIXTURES_DIR / "basic_slides.pptx"), ".", "--json"],
     "search_basic_slides.json", "json"),

    # TOC
    ("toc", [str(FIXTURES_DIR / "basic_slides.pptx"), "--json"],
     "toc_basic_slides.json", "json"),
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


def _build_and_validate_with_action(fixture_name: str, *action_args: str) -> tuple[bool, dict | str]:
    with tempfile.TemporaryDirectory() as tmp:
        unpacked = Path(tmp) / "unpacked"
        out_pptx = Path(tmp) / "out.pptx"

        subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "ooxml" / "unpack.py"),
                str(FIXTURES_DIR / fixture_name),
                str(unpacked),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = subprocess.run([sys.executable, str(SCRIPT_DIR / "add_slide.py"), str(unpacked), *action_args], check=True, capture_output=True, text=True)
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "ooxml" / "pack.py"),
                str(unpacked),
                str(out_pptx),
                "--original",
                str(FIXTURES_DIR / fixture_name),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(SCRIPT_DIR))
        from ooxml.validate import validate

        vresult = validate(str(out_pptx))
        return vresult["passed"], vresult if vresult["passed"] else result.stdout.strip() or json.dumps(vresult)


def run_add_slide_blank_regression() -> tuple[bool, str]:
    """Verify add_slide.py --blank validates on the shipped basic fixture."""
    ok, payload = _build_and_validate_with_action("basic_slides.pptx", "--blank")
    return ok, json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else str(payload)


def run_add_slide_blank_blankless_regression() -> tuple[bool, str]:
    ok, payload = _build_and_validate_with_action("blankless_minimal_deck.pptx", "--blank")
    return ok, json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else str(payload)


def run_add_slide_blank_nonstandard_name_regression() -> tuple[bool, str]:
    ok, payload = _build_and_validate_with_action("blank_layout_named_nonstandard.pptx", "--blank")
    return ok, json.dumps(payload, ensure_ascii=False) if isinstance(payload, dict) else str(payload)


def run_duplicate_slide_media_chart_regression() -> tuple[bool, str]:
    ok, payload = _build_and_validate_with_action("duplicate_media_chart_deck.pptx", "--duplicate", "1")
    if not ok:
        return False, str(payload)

    with tempfile.TemporaryDirectory() as tmp:
        unpacked = Path(tmp) / "unpacked"
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "ooxml" / "unpack.py"),
                str(FIXTURES_DIR / "duplicate_media_chart_deck.pptx"),
                str(unpacked),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "add_slide.py"), str(unpacked), "--duplicate", "1"],
            check=True,
            capture_output=True,
            text=True,
        )
        rels = (unpacked / "ppt" / "slides" / "_rels" / "slide2.xml.rels").read_text(encoding="utf-8")
        summary = {
            "has_chart_rel": "relationships/chart" in rels,
            "has_image_rel": "relationships/image" in rels,
        }
    return _compare_expected(summary, "duplicate_media_chart_summary.json", "json")


def run_notes_reuse_conflict_regression() -> tuple[bool, str]:
    sys.path.insert(0, str(SCRIPT_DIR))
    from ooxml.validate import validate

    result = validate(str(FIXTURES_DIR / "notes_reuse_conflict.pptx"))
    return _compare_expected(result, "notes_reuse_conflict.json", "json")


UNIT_TESTS: list[tuple[str, callable]] = [
    ("add-slide:blank_basic_fixture", run_add_slide_blank_regression),
    ("add-slide:blank_blankless_fixture", run_add_slide_blank_blankless_regression),
    ("add-slide:blank_nonstandard_name_fixture", run_add_slide_blank_nonstandard_name_regression),
    ("duplicate-slide:media_chart_fixture", run_duplicate_slide_media_chart_regression),
    ("validate:notes_reuse_conflict_fixture", run_notes_reuse_conflict_regression),
]


def run_cli(command: str, args: list[str], mode: str = "text") -> str:
    """Run pptx_cli.py and capture output."""
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
    parser = argparse.ArgumentParser(description="Regression test runner for pptx_cli.py")
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
