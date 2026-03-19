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

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
