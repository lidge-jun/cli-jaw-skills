#!/usr/bin/env python3
"""Regression test runner for hwpx_cli.py.

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
CLI = SCRIPT_DIR / "hwpx_cli.py"

# (command, args, expected_file, compare_mode)
# compare_mode: "json" = parse+compare dicts, "text" = strip+compare strings
TEST_CASES: list[tuple[str, list[str], str, str]] = [
    # Agentic Reading
    ("toc", [str(FIXTURES_DIR / "agentic/heading_gonmun.hwpx"), "--json"],
     "heading_gonmun_toc.json", "json"),
    ("chunk", [str(FIXTURES_DIR / "agentic/heading_gonmun.hwpx"), "--json"],
     "heading_gonmun_chunks.json", "json"),
    ("search-chunks", [str(FIXTURES_DIR / "agentic/heading_gonmun.hwpx"), "시장", "--json"],
     "heading_gonmun_search_market.json", "json"),

    # Repair dry-run
    ("repair", [str(FIXTURES_DIR / "repair/normal_valid.hwpx")],
     "repair_dryrun_normal_valid.txt", "text"),
    ("repair", [str(FIXTURES_DIR / "repair/normal_valid_2.hwpx")],
     "repair_dryrun_normal_valid_2.txt", "text"),
    ("repair", [str(FIXTURES_DIR / "repair/missing_xml_decl.hwpx")],
     "repair_dryrun_missing_xml_decl.txt", "text"),
    ("repair", [str(FIXTURES_DIR / "repair/invalid_idref.hwpx")],
     "repair_dryrun_invalid_idref.txt", "text"),
    ("repair", [str(FIXTURES_DIR / "repair/stale_linesegarray.hwpx")],
     "repair_dryrun_stale_linesegarray.txt", "text"),
    ("repair", [str(FIXTURES_DIR / "repair/unclosed_tag.hwpx")],
     "repair_dryrun_unclosed_tag.txt", "text"),

    # Content-check (smoke test using existing fixture)
    ("content-check", [str(FIXTURES_DIR / "agentic/heading_gonmun.hwpx"),
     "--must-have", "시장", "--json"],
     "content_check_must_have.json", "json"),
    ("content-check", [str(FIXTURES_DIR / "agentic/heading_gonmun.hwpx"),
     "--must-not-have", "ZZZZNOTEXIST", "--json"],
     "content_check_must_not_have.json", "json"),
]


def run_cli(command: str, args: list[str], mode: str = "text") -> str:
    """Run hwpx_cli.py and capture output.

    For JSON mode: stdout only (stderr has count messages).
    For text mode: combined stdout+stderr.
    """
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
    parser = argparse.ArgumentParser(description="Regression test runner for hwpx_cli.py")
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
