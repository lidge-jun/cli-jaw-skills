#!/usr/bin/env python3
"""Convert pandas ``orient='split'`` JSON into OfficeCLI batch set commands.

The converter intentionally bypasses ``officecli import``. Each non-null value is
written to an explicit cell, which is the safe Windows bulk-write path and keeps
embedded newlines inside a single JSON string.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Iterable


def excel_column(index: int) -> str:
    """Return the 1-based Excel column name for *index*."""
    if index < 1:
        raise ValueError("column index must be >= 1")
    chars: list[str] = []
    while index:
        index, remainder = divmod(index - 1, 26)
        chars.append(chr(ord("A") + remainder))
    return "".join(reversed(chars))


def parse_sheet_spec(spec: str) -> tuple[str, Path]:
    if "=" not in spec:
        raise ValueError("--sheet-json must use SHEET=PATH")
    sheet, raw_path = spec.split("=", 1)
    sheet = sheet.strip()
    if not sheet or "/" in sheet:
        raise ValueError(f"invalid sheet name: {sheet!r}")
    path = Path(raw_path).expanduser()
    return sheet, path


def officecli_props(value: Any) -> dict[str, str] | None:
    """Map one JSON scalar to OfficeCLI string props, skipping null/NaN cells."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, bool):
        return {"value": "true" if value else "false"}
    if isinstance(value, (int, float)):
        return {"value": str(value), "type": "number"}
    if isinstance(value, str):
        return {"value": value}
    raise ValueError(f"unsupported cell value type: {type(value).__name__}")


def commands_for_split_payload(sheet: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    columns = payload.get("columns")
    rows = payload.get("data")
    if not isinstance(columns, list) or not isinstance(rows, list):
        raise ValueError("expected pandas orient='split' JSON with columns and data arrays")

    commands: list[dict[str, Any]] = []
    table: Iterable[tuple[int, list[Any]]] = [(1, columns)]
    table = [*table, *((row_index + 2, row) for row_index, row in enumerate(rows))]
    for row_number, row in table:
        if not isinstance(row, list):
            raise ValueError(f"row {row_number} is not an array")
        if len(row) != len(columns):
            raise ValueError(
                f"row {row_number} has {len(row)} cells; expected {len(columns)}"
            )
        for column_index, value in enumerate(row, start=1):
            props = officecli_props(value)
            if props is None:
                continue
            commands.append(
                {
                    "command": "set",
                    "path": f"/{sheet}/{excel_column(column_index)}{row_number}",
                    "props": props,
                }
            )
    return commands


def load_commands(specs: Iterable[str]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for spec in specs:
        sheet, path = parse_sheet_spec(spec)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"{path} must contain a JSON object")
        commands.extend(commands_for_split_payload(sheet, payload))
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sheet-json",
        action="append",
        required=True,
        metavar="SHEET=PATH",
        help="pandas orient='split' JSON input; repeat for multiple sheets",
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    commands = load_commands(args.sheet_json)
    if not commands:
        raise SystemExit("refusing to write an empty OfficeCLI batch")
    args.output.write_text(
        json.dumps(commands, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(commands)} explicit cell commands to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
