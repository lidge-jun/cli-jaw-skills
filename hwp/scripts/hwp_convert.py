#!/usr/bin/env python3
"""Convert HWP 5.0 binary files to HWPX using neolord0/hwp2hwpx Java sidecar.

Handles JDK/Maven detection, sidecar build caching, and conversion in one command.

Usage:
    python hwp_convert.py input.hwp output.hwpx
    python hwp_convert.py input.hwp                    # output = input.hwpx
    python hwp_convert.py input.hwp -o output.hwpx --verify

Requirements:
    - Java 11+ (java on PATH)
    - Maven 3+ (mvn on PATH)
    - Internet access (first run only, to clone + build)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

SIDECAR_DIR = Path("/tmp/hwp2hwpx")
SIDECAR_REPO = "https://github.com/neolord0/hwp2hwpx"
MAIN_CLASS = "CliRunner"

# Minimal CLI runner — hwp2hwpx is a library with no main method
_CLI_RUNNER_SRC = """\
import kr.dogfoot.hwp2hwpx.Hwp2Hwpx;
import kr.dogfoot.hwplib.object.HWPFile;
import kr.dogfoot.hwplib.reader.HWPReader;
import kr.dogfoot.hwpxlib.object.HWPXFile;
import kr.dogfoot.hwpxlib.writer.HWPXWriter;

public class CliRunner {
    public static void main(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: CliRunner input.hwp output.hwpx");
            System.exit(1);
        }
        HWPFile hwp = HWPReader.fromFile(args[0]);
        HWPXFile hwpx = Hwp2Hwpx.toHWPX(hwp);
        HWPXWriter.toFilepath(hwpx, args[1]);
        System.out.println("OK: " + args[0] + " -> " + args[1]);
    }
}
"""


def _check_tool(name: str) -> bool:
    return shutil.which(name) is not None


def _patch_pom_source_target(pom_path: Path) -> None:
    """Patch pom.xml source/target from 7 to 11 for modern JDKs."""
    text = pom_path.read_text()
    if "<source>7</source>" in text:
        text = text.replace("<source>7</source>", "<source>11</source>")
        text = text.replace("<target>7</target>", "<target>11</target>")
        pom_path.write_text(text)
        print("Patched pom.xml: source/target 7 → 11", file=sys.stderr)


def _ensure_sidecar() -> Path:
    """Clone, patch, inject CLI runner, and build hwp2hwpx."""
    classes_dir = SIDECAR_DIR / "target" / "classes"
    deps_dir = SIDECAR_DIR / "target" / "dependency"
    runner_class = classes_dir / "CliRunner.class"

    if classes_dir.exists() and deps_dir.exists() and runner_class.exists():
        return SIDECAR_DIR

    print("Building hwp2hwpx sidecar (first run only)...", file=sys.stderr)

    if not SIDECAR_DIR.exists():
        subprocess.run(
            ["git", "clone", SIDECAR_REPO, str(SIDECAR_DIR)],
            check=True, capture_output=True, text=True,
        )

    # Patch source/target for JDK 17+
    pom_path = SIDECAR_DIR / "pom.xml"
    if pom_path.exists():
        _patch_pom_source_target(pom_path)

    subprocess.run(
        ["mvn", "-DskipTests", "package", "dependency:copy-dependencies"],
        cwd=str(SIDECAR_DIR), check=True, capture_output=True, text=True,
    )

    if not classes_dir.exists():
        raise RuntimeError("Maven build succeeded but target/classes not found")

    # Inject CLI runner
    runner_src = SIDECAR_DIR / "CliRunner.java"
    runner_src.write_text(_CLI_RUNNER_SRC)
    cp = _build_classpath(SIDECAR_DIR)
    subprocess.run(
        ["javac", "-cp", cp, str(runner_src), "-d", str(classes_dir)],
        check=True, capture_output=True, text=True,
    )
    runner_src.unlink()

    print("Sidecar built successfully.", file=sys.stderr)
    return SIDECAR_DIR


def _build_classpath(sidecar: Path) -> str:
    classes = str(sidecar / "target" / "classes")
    deps = str(sidecar / "target" / "dependency" / "*")
    return f"{classes}:{deps}"


def convert(input_hwp: str, output_hwpx: str, verify: bool = True) -> int:
    """Convert HWP to HWPX. Returns 0 on success, 1 on failure."""
    input_path = Path(input_hwp).resolve()
    output_path = Path(output_hwpx).resolve()

    if not input_path.exists():
        print(f"Error: {input_hwp} does not exist", file=sys.stderr)
        return 1

    # Check prerequisites
    for tool in ("java", "mvn"):
        if not _check_tool(tool):
            print(f"Error: {tool} not found on PATH. Install JDK 11+ and Maven.", file=sys.stderr)
            return 1

    # Build sidecar
    try:
        sidecar = _ensure_sidecar()
    except (subprocess.CalledProcessError, RuntimeError) as e:
        print(f"Error building sidecar: {e}", file=sys.stderr)
        return 1

    # Run conversion
    cp = _build_classpath(sidecar)
    result = subprocess.run(
        ["java", "-cp", cp, MAIN_CLASS, str(input_path), str(output_path)],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print(f"Error: conversion failed\n{result.stderr}", file=sys.stderr)
        return 1

    if not output_path.exists():
        print("Error: output file was not created", file=sys.stderr)
        return 1

    # Verify
    if verify:
        try:
            with zipfile.ZipFile(str(output_path), "r") as zf:
                if "Contents/section0.xml" not in zf.namelist():
                    print("Warning: section0.xml not found in output", file=sys.stderr)
                    return 1
                section = zf.read("Contents/section0.xml").decode("utf-8")
                if "이 문서는 HWP 파일입니다" in section:
                    print("Error: output contains dummy text — conversion failed", file=sys.stderr)
                    return 1
        except zipfile.BadZipFile:
            print("Error: output is not a valid ZIP/HWPX file", file=sys.stderr)
            return 1

    print(f"Converted: {input_hwp} -> {output_hwpx}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert HWP 5.0 to HWPX via hwp2hwpx sidecar")
    parser.add_argument("input", help="Input .hwp file")
    parser.add_argument("output", nargs="?", help="Output .hwpx file (default: same name with .hwpx)")
    parser.add_argument("-o", "--output-file", help="Output .hwpx file (alternative to positional)")
    parser.add_argument("--no-verify", action="store_true", help="Skip post-conversion verification")
    args = parser.parse_args()

    output = args.output_file or args.output
    if not output:
        output = str(Path(args.input).with_suffix(".hwpx"))

    return convert(args.input, output, verify=not args.no_verify)


if __name__ == "__main__":
    raise SystemExit(main())
