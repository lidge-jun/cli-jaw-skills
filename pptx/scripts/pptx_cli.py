#!/usr/bin/env python3
"""Unified CLI for PPTX document operations.

Subcommands:
    open            Unpack PPTX to directory with pretty-printed XML
    save            Pack directory to PPTX
    validate        Structural validation (JSON output)
    repair          Auto-repair common issues (dry-run by default)
    text            Extract text from PPTX
    thumbnail       Generate slide thumbnail grid or individual PNGs
    add-slide       Add blank or duplicate slide (operates on unpacked dir)
    clean           Find/remove orphaned files (operates on unpacked dir)
    export-pdf      Convert PPTX to PDF via LibreOffice
    search          Search text across slides (presentation order)
    toc             Extract slide titles as table of contents

Usage:
    python pptx_cli.py open input.pptx work/
    python pptx_cli.py save work/ output.pptx
    python pptx_cli.py validate input.pptx
    python pptx_cli.py validate input.pptx --json
    python pptx_cli.py repair input.pptx
    python pptx_cli.py repair input.pptx --apply -o out.pptx
    python pptx_cli.py text input.pptx
    python pptx_cli.py thumbnail input.pptx out.png
    python pptx_cli.py thumbnail input.pptx out_dir/ --individual
    python pptx_cli.py add-slide work/ --blank
    python pptx_cli.py add-slide work/ --duplicate 3 --position 1
    python pptx_cli.py clean work/
    python pptx_cli.py clean work/ --delete
    python pptx_cli.py export-pdf input.pptx output.pdf
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_REF_DIR = SCRIPT_DIR.parent.parent  # ooxml_core lives here

# DrawingML namespace for text elements
ANS = "http://schemas.openxmlformats.org/drawingml/2006/main"
# PresentationML namespace
PNS = "http://schemas.openxmlformats.org/presentationml/2006/main"
# Relationships namespace
RNS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unpack_to_tmpdir(pptx_path: str) -> str:
    """Unpack PPTX to a temp directory, return path."""
    tmpdir = tempfile.mkdtemp(prefix="pptx_cli_")
    with zipfile.ZipFile(pptx_path, "r") as zf:
        zf.extractall(tmpdir)
    return tmpdir


def _slide_files(pptx_path: str) -> list[str]:
    """List slide XML filenames inside PPTX (filename sorted, for legacy use)."""
    with zipfile.ZipFile(pptx_path, "r") as zf:
        return sorted(
            n for n in zf.namelist()
            if n.startswith("ppt/slides/slide") and n.endswith(".xml")
        )


def _ordered_slide_files(pptx_path: str) -> list[tuple[int, str]]:
    """Return slides in presentation order as [(display_num, filename), ...].

    Reads ppt/presentation.xml for ordering via sldIdLst,
    then resolves rId -> filename via ppt/_rels/presentation.xml.rels.
    Falls back to filename sort if presentation.xml is missing.
    """
    from xml.etree import ElementTree as ET

    try:
        with zipfile.ZipFile(pptx_path, "r") as zf:
            # 1. Parse rels to build rId -> filename map
            rels_xml = zf.read("ppt/_rels/presentation.xml.rels")
            rels_root = ET.fromstring(rels_xml)
            rid_to_file: dict[str, str] = {}
            for rel in rels_root:
                rid = rel.get("Id", "")
                target = rel.get("Target", "")
                if target.startswith("slides/"):
                    rid_to_file[rid] = f"ppt/{target}"

            # 2. Parse presentation.xml for slide order
            pres_xml = zf.read("ppt/presentation.xml")
            pres_root = ET.fromstring(pres_xml)
            ordered: list[tuple[int, str]] = []
            for i, sld_id in enumerate(pres_root.iter(f"{{{PNS}}}sldId")):
                rid = sld_id.get(f"{{{RNS}}}id")
                if rid and rid in rid_to_file:
                    ordered.append((i + 1, rid_to_file[rid]))

        if ordered:
            return ordered
    except (KeyError, ET.ParseError):
        pass

    # Fallback: filename sort
    return [(i + 1, n) for i, n in enumerate(_slide_files(pptx_path))]


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_open(args: argparse.Namespace) -> int:
    """Unpack PPTX with pretty-printed XML."""
    sys.path.insert(0, str(SKILLS_REF_DIR))
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from ooxml_core.unpack import unpack
    except ImportError:
        from ooxml.unpack import unpack
    msg = unpack(args.input, args.output_dir)
    print(msg)
    return 1 if msg.startswith("Error") else 0


def cmd_save(args: argparse.Namespace) -> int:
    """Pack directory to PPTX."""
    sys.path.insert(0, str(SKILLS_REF_DIR))
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from ooxml_core.pack import pack
    except ImportError:
        from ooxml.pack import pack
    msg = pack(args.input_dir, args.output)
    print(msg)
    return 1 if msg.startswith("Error") else 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Structural validation."""
    sys.path.insert(0, str(SKILLS_REF_DIR))
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from ooxml_core.validate import validate
    except ImportError:
        from ooxml.validate import validate
    result = validate(args.input, verbose=not args.json)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not result["passed"]:
            for e in result["errors"]:
                print(f"  ERROR: {e}")
            for w in result["warnings"]:
                print(f"  WARN:  {w}")
    return 0 if result["passed"] else 1


def cmd_repair(args: argparse.Namespace) -> int:
    """Auto-repair common OOXML issues (dry-run by default)."""
    apply = args.apply or args.output is not None
    dry_run = not apply

    work = _unpack_to_tmpdir(args.input)
    try:
        sys.path.insert(0, str(SKILLS_REF_DIR))
        sys.path.insert(0, str(SCRIPT_DIR))
        try:
            from ooxml_core.repair import repair
        except ImportError:
            from ooxml.repair import repair
        result = repair(work, dry_run=dry_run)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result["repaired"] > 0:
                label = "REPAIRED" if apply else "WOULD REPAIR"
                print(f"{label} ({result['repaired']} issue(s)):")
                for d in result["details"]:
                    print(f"  - {d}")
            else:
                print("No issues found.")

        if apply and result["repaired"] > 0:
            try:
                from ooxml_core.pack import pack
            except ImportError:
                from ooxml.pack import pack
            output = args.output or args.input
            if not args.output:
                backup = Path(args.input).with_suffix(".pptx.bak")
                if not backup.exists():
                    shutil.copy2(args.input, backup)
                    print(f"Backup: {backup}")
            pack(work, output)
            print(f"Output: {output}")

            try:
                from ooxml_core.validate import validate
            except ImportError:
                from ooxml.validate import validate
            vresult = validate(output)
            if vresult["passed"]:
                print("Post-repair validation: PASS")
            else:
                print("WARNING: post-repair validation issues:", file=sys.stderr)
                for e in vresult["errors"]:
                    print(f"  - {e}", file=sys.stderr)

        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_text(args: argparse.Namespace) -> int:
    """Extract text from PPTX slides."""
    from xml.etree import ElementTree as ET

    for slide_name in _slide_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = ET.fromstring(zf.read(slide_name))

        # Extract slide number from filename
        slide_num = slide_name.split("slide")[-1].replace(".xml", "")
        texts = []
        for t in root.iter(f"{{{ANS}}}t"):
            if t.text and t.text.strip():
                texts.append(t.text)
        if texts:
            print(f"--- Slide {slide_num} ---")
            for text in texts:
                print(text)
    return 0


def cmd_thumbnail(args: argparse.Namespace) -> int:
    """Generate slide thumbnails."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from thumbnail import create_thumbnails
    msg = create_thumbnails(
        args.input, args.output,
        cols=args.cols, dpi=args.dpi, individual=args.individual,
    )
    print(msg)
    return 1 if msg.startswith("Error") else 0


def cmd_add_slide(args: argparse.Namespace) -> int:
    """Add blank or duplicate slide."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from add_slide import add_blank_slide, duplicate_slide

    if args.blank:
        msg = add_blank_slide(args.unpacked_dir, position=args.position)
    else:
        msg = duplicate_slide(args.unpacked_dir, args.duplicate, position=args.position)
    print(msg)
    return 1 if msg.startswith("Error") else 0


def cmd_clean(args: argparse.Namespace) -> int:
    """Find/remove orphaned files."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from clean import clean
    result = clean(args.unpacked_dir, delete=args.delete)
    print(result)
    return 0


def cmd_export_pdf(args: argparse.Namespace) -> int:
    """Convert PPTX to PDF via LibreOffice."""
    sys.path.insert(0, str(SKILLS_REF_DIR))
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from ooxml_core.soffice import run_soffice
    except ImportError:
        from ooxml.soffice import run_soffice

    src = Path(args.input).resolve()
    dst = Path(args.output).resolve()

    if not src.exists():
        print(f"Error: {args.input} does not exist", file=sys.stderr)
        return 1

    try:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_soffice(
                [
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", tmp,
                    str(src),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            pdf_files = list(Path(tmp).glob("*.pdf"))
            if not pdf_files:
                print(f"Error: PDF conversion failed. stderr: {result.stderr}", file=sys.stderr)
                return 1

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf_files[0], dst)

        print(f"Exported: {args.input} -> {args.output}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Search text content across slides with regex."""
    import re
    from xml.etree import ElementTree as ET

    pattern = re.compile(args.pattern)
    results: list[dict] = []

    for display_num, slide_name in _ordered_slide_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = ET.fromstring(zf.read(slide_name))

        # Collect text per shape (sp) for context
        for sp in root.iter(f"{{{PNS}}}sp"):
            texts = []
            for t in sp.iter(f"{{{ANS}}}t"):
                if t.text:
                    texts.append(t.text)
            full_text = "".join(texts)
            if pattern.search(full_text):
                results.append({
                    "slide": slide_name,
                    "slide_num": display_num,
                    "text": full_text[:120],
                })

    if not results:
        print("No matches found.", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"slide{r['slide_num']}: {r['text']}")
    print(f"\n{len(results)} match(es) found.", file=sys.stderr)
    return 0


def _get_slide_title(root) -> str:
    """Extract title text from a slide XML root."""
    from xml.etree import ElementTree as ET

    # Find shape with title placeholder
    for sp in root.iter(f"{{{PNS}}}sp"):
        for ph in sp.iter(f"{{{PNS}}}ph"):
            ph_type = ph.get("type", "")
            if ph_type in ("title", "ctrTitle"):
                texts = []
                for t in sp.iter(f"{{{ANS}}}t"):
                    if t.text:
                        texts.append(t.text)
                return "".join(texts).strip()

    # Fallback: first non-empty text in slide
    for t in root.iter(f"{{{ANS}}}t"):
        if t.text and t.text.strip():
            return t.text.strip()
    return "(untitled)"


def cmd_toc(args: argparse.Namespace) -> int:
    """Extract slide titles as table of contents."""
    from xml.etree import ElementTree as ET

    toc = []
    for display_num, slide_name in _ordered_slide_files(args.input):
        with zipfile.ZipFile(args.input, "r") as zf:
            root = ET.fromstring(zf.read(slide_name))

        title = _get_slide_title(root)
        toc.append({"slide_num": display_num, "title": title})

    if args.json:
        print(json.dumps(toc, ensure_ascii=False, indent=2))
    else:
        for entry in toc:
            print(f"slide{entry['slide_num']}: {entry['title']}")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified CLI for PPTX document operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # open
    p = sub.add_parser("open", help="Unpack PPTX to directory with pretty-printed XML")
    p.add_argument("input", help="Input .pptx file")
    p.add_argument("output_dir", help="Output directory")

    # save
    p = sub.add_parser("save", help="Pack directory to PPTX")
    p.add_argument("input_dir", help="Input directory")
    p.add_argument("output", help="Output .pptx file")

    # validate
    p = sub.add_parser("validate", help="Structural validation")
    p.add_argument("input", help="Input .pptx file or unpacked directory")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # repair
    p = sub.add_parser("repair", help="Auto-repair (dry-run by default)")
    p.add_argument("input", help="Input .pptx file")
    p.add_argument("--apply", action="store_true", help="Apply repairs (default: dry-run)")
    p.add_argument("-o", "--output", help="Output file (implies --apply)")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # text
    p = sub.add_parser("text", help="Extract text from PPTX slides")
    p.add_argument("input", help="Input .pptx file")

    # thumbnail
    p = sub.add_parser("thumbnail", help="Generate slide thumbnails")
    p.add_argument("input", help="Input .pptx file")
    p.add_argument("output", help="Output PNG file or directory (with --individual)")
    p.add_argument("--cols", type=int, default=4, help="Columns in grid (default: 4)")
    p.add_argument("--dpi", type=int, default=150, help="DPI for rendering (default: 150)")
    p.add_argument("--individual", action="store_true", help="Save individual slide PNGs")

    # add-slide
    p = sub.add_parser("add-slide", help="Add or duplicate slides (unpacked dir)")
    p.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    p.add_argument("--position", type=int, help="Insert position (1-based)")
    slide_group = p.add_mutually_exclusive_group(required=True)
    slide_group.add_argument("--blank", action="store_true", help="Add a blank slide")
    slide_group.add_argument("--duplicate", type=int, metavar="N", help="Duplicate slide N")

    # clean
    p = sub.add_parser("clean", help="Find/remove orphaned files (unpacked dir)")
    p.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    p.add_argument("--delete", action="store_true", help="Actually delete orphaned files")

    # export-pdf
    p = sub.add_parser("export-pdf", help="Convert PPTX to PDF via LibreOffice")
    p.add_argument("input", help="Input .pptx file")
    p.add_argument("output", help="Output .pdf file")

    # search
    p = sub.add_parser("search", help="Search text across slides")
    p.add_argument("input", help="Input .pptx file")
    p.add_argument("pattern", help="Regex pattern to search")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # toc
    p = sub.add_parser("toc", help="Extract slide titles as table of contents")
    p.add_argument("input", help="Input .pptx file")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    args = parser.parse_args()

    commands = {
        "open": cmd_open,
        "save": cmd_save,
        "validate": cmd_validate,
        "repair": cmd_repair,
        "text": cmd_text,
        "thumbnail": cmd_thumbnail,
        "add-slide": cmd_add_slide,
        "clean": cmd_clean,
        "export-pdf": cmd_export_pdf,
        "search": cmd_search,
        "toc": cmd_toc,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
