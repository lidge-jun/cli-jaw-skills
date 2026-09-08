#!/usr/bin/env python3
"""Fail unless OfficeCLI reads exact expected values from a closed workbook."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Callable


def value_candidates(value: Any) -> list[str]:
    """Collect semantic cell values from OfficeCLI's JSON response shapes."""
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"text", "value", "rawValue", "displayValue"} and isinstance(
                item, (str, int, float, bool)
            ):
                found.append(str(item))
            found.extend(value_candidates(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(value_candidates(item))
    return found


def verify_cells(
    workbook: str,
    expectations: dict[str, Any],
    officecli: str = "officecli",
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> list[tuple[str, str]]:
    if not expectations:
        raise ValueError("at least one persisted cell expectation is required")
    verified: list[tuple[str, str]] = []
    for cell_path, expected_value in expectations.items():
        expected = str(expected_value)
        result = run(
            [officecli, "get", workbook, cell_path, "--json"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"persisted read-back failed for {cell_path} (exit {result.returncode}): "
                f"{result.stderr.strip()}"
            )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"non-JSON read-back for {cell_path}: {error}") from error
        candidates = value_candidates(payload)
        if expected not in candidates:
            raise RuntimeError(
                f"persisted value mismatch for {cell_path}: expected {expected!r}; "
                f"read-back candidates={candidates!r}"
            )
        verified.append((cell_path, expected))
    return verified


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook")
    parser.add_argument(
        "--expect-json",
        required=True,
        type=Path,
        help="JSON object mapping OfficeCLI cell paths to exact expected values",
    )
    parser.add_argument("--officecli", default=os.environ.get("OFFICECLI_BIN", "officecli"))
    args = parser.parse_args()

    expectations = json.loads(args.expect_json.read_text(encoding="utf-8"))
    if not isinstance(expectations, dict):
        raise SystemExit("--expect-json must contain a JSON object")
    for cell_path, expected in verify_cells(
        args.workbook, expectations, officecli=args.officecli
    ):
        print(f"verified {cell_path}={expected!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
