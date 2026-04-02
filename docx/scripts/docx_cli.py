#!/usr/bin/env python3
"""Unified CLI for DOCX document operations.

Subcommands:
    open            Unpack DOCX to directory with pretty-printed XML
    save            Pack directory to DOCX
    validate        Structural validation (JSON output)
    repair          Auto-repair common issues (dry-run by default)
    text            Extract text from DOCX
    search          Search text content with regex
    toc             Extract heading-based table of contents
    chunk           Split document into chunks for agentic reading
    search-chunks   Search within heading-based chunks
    comment         Add comments to DOCX
    accept-changes  Accept all tracked changes
    merge-runs      Merge adjacent runs with identical formatting

Usage:
    python docx_cli.py open input.docx work/
    python docx_cli.py save work/ output.docx
    python docx_cli.py validate input.docx
    python docx_cli.py validate input.docx --json
    python docx_cli.py repair input.docx
    python docx_cli.py repair input.docx --apply -o out.docx
    python docx_cli.py text input.docx
    python docx_cli.py search input.docx "pattern"
    python docx_cli.py toc input.docx --json
    python docx_cli.py chunk input.docx --json
    python docx_cli.py chunk input.docx --by size --max-chars 3000
    python docx_cli.py search-chunks input.docx "pattern" --json
    python docx_cli.py comment in.docx out.docx --text "Review" --anchor "target"
    python docx_cli.py comment in.docx out.docx --json comments.json
    python docx_cli.py accept-changes in.docx out.docx
    python docx_cli.py merge-runs unpacked/
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
SKILLS_REF_DIR = SCRIPT_DIR.parent.parent  # ooxml_core lives here

WNS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unpack_to_tmpdir(docx_path: str) -> str:
    """Unpack DOCX to a temp directory, return path."""
    tmpdir = tempfile.mkdtemp(prefix="docx_cli_")
    with zipfile.ZipFile(docx_path, "r") as zf:
        zf.extractall(tmpdir)
    return tmpdir


def _get_document_xml(docx_path: str) -> ET.Element:
    """Read and parse word/document.xml from DOCX ZIP."""
    with zipfile.ZipFile(docx_path, "r") as zf:
        return ET.fromstring(zf.read("word/document.xml"))


def _get_all_text(root: ET.Element) -> list[str]:
    """Extract all w:t text from an element tree."""
    texts = []
    for t in root.iter(f"{{{WNS}}}t"):
        if t.text:
            texts.append(t.text)
    return texts


def _get_para_text(para: ET.Element) -> str:
    """Get concatenated text from a paragraph's w:t elements."""
    parts = []
    for t in para.iter(f"{{{WNS}}}t"):
        if t.text:
            parts.append(t.text)
    return "".join(parts)


def _get_heading_level(para: ET.Element) -> int | None:
    """Return heading level (0-based) from paragraph style or outlineLvl.

    Detects:
      - pStyle val="Heading1" .. "Heading9"  → level 0..8
      - pStyle val="heading 1" .. "heading 9" (case-insensitive)
      - outlineLvl val="N" inside pPr        → level N
    Returns None if the paragraph is not a heading.
    """
    ppr = para.find(f"{{{WNS}}}pPr")
    if ppr is None:
        return None

    # Check pStyle
    pstyle = ppr.find(f"{{{WNS}}}pStyle")
    if pstyle is not None:
        val = (pstyle.get(f"{{{WNS}}}val") or pstyle.get("val") or "").lower()
        for prefix in ("heading", "heading "):
            if val.startswith(prefix):
                rest = val[len(prefix):]
                if rest.isdigit():
                    return int(rest) - 1

    # Check outlineLvl
    outline = ppr.find(f"{{{WNS}}}outlineLvl")
    if outline is not None:
        val = outline.get(f"{{{WNS}}}val") or outline.get("val") or ""
        if val.isdigit() and int(val) < 9:
            return int(val)

    return None


def _build_toc(docx_path: str) -> list[dict]:
    """Build table of contents from heading paragraphs."""
    root = _get_document_xml(docx_path)
    toc: list[dict] = []
    for i, para in enumerate(root.iter(f"{{{WNS}}}p")):
        level = _get_heading_level(para)
        if level is not None:
            text = _get_para_text(para).strip()
            if text:
                toc.append({
                    "level": level,
                    "title": text,
                    "para_index": i,
                })
    return toc


def _build_chunks(
    docx_path: str,
    by: str = "heading",
    max_chars: int = 4000,
) -> list[dict]:
    """Split document into chunks for agentic reading."""
    root = _get_document_xml(docx_path)
    all_paras = list(root.iter(f"{{{WNS}}}p"))

    # Check if headings exist; fallback to size if none
    has_headings = any(_get_heading_level(p) is not None for p in all_paras)
    if by == "heading" and not has_headings:
        by = "size"

    chunks: list[dict] = []
    chunk_id = 0

    if by == "heading":
        current: dict = {
            "id": chunk_id, "title": "(intro)", "start_para": 0,
            "texts": [], "char_count": 0,
        }

        for i, p in enumerate(all_paras):
            text = _get_para_text(p)
            level = _get_heading_level(p)

            if level is not None and current["texts"]:
                current["end_para"] = i - 1
                current["preview"] = current["texts"][0][:80] if current["texts"] else ""
                del current["texts"]
                chunks.append(current)
                chunk_id += 1
                current = {
                    "id": chunk_id, "title": text.strip(),
                    "start_para": i, "texts": [], "char_count": 0,
                }

            current["texts"].append(text)
            current["char_count"] += len(text)

        if current["texts"]:
            current["end_para"] = len(all_paras) - 1
            current["preview"] = current["texts"][0][:80] if current["texts"] else ""
            del current["texts"]
            chunks.append(current)

    else:  # size
        current = {
            "id": chunk_id, "title": f"chunk-{chunk_id}",
            "start_para": 0, "texts": [], "char_count": 0,
        }

        for i, p in enumerate(all_paras):
            text = _get_para_text(p)

            if current["char_count"] + len(text) > max_chars and current["texts"]:
                current["end_para"] = i - 1
                current["preview"] = current["texts"][0][:80] if current["texts"] else ""
                del current["texts"]
                chunks.append(current)
                chunk_id += 1
                current = {
                    "id": chunk_id, "title": f"chunk-{chunk_id}",
                    "start_para": i, "texts": [], "char_count": 0,
                }

            current["texts"].append(text)
            current["char_count"] += len(text)

        if current["texts"]:
            current["end_para"] = len(all_paras) - 1
            current["preview"] = current["texts"][0][:80] if current["texts"] else ""
            del current["texts"]
            chunks.append(current)

    return chunks


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_open(args: argparse.Namespace) -> int:
    """Unpack DOCX with pretty-printed XML."""
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
    """Pack directory to DOCX."""
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
                backup = Path(args.input).with_suffix(".docx.bak")
                if not backup.exists():
                    shutil.copy2(args.input, backup)
                    print(f"Backup: {backup}")
            msg = pack(work, output)
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
    """Extract text from DOCX."""
    try:
        root = _get_document_xml(args.input)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    for para in root.iter(f"{{{WNS}}}p"):
        text = _get_para_text(para)
        if text.strip():
            print(text)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """Search text content with regex."""
    try:
        root = _get_document_xml(args.input)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    pattern = re.compile(args.pattern)
    found = 0
    for i, para in enumerate(root.iter(f"{{{WNS}}}p")):
        text = _get_para_text(para)
        if pattern.search(text):
            print(f"p{i}: {text[:120]}")
            found += 1

    if found == 0:
        print("No matches found.", file=sys.stderr)
        return 1
    print(f"\n{found} match(es) found.", file=sys.stderr)
    return 0


def cmd_toc(args: argparse.Namespace) -> int:
    """Extract heading-based table of contents."""
    try:
        toc = _build_toc(args.input)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

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
    try:
        chunks = _build_chunks(args.input, by=args.by, max_chars=args.max_chars)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

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
    """Search within heading-based chunks for contextual results."""
    try:
        root = _get_document_xml(args.input)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    chunks_meta = _build_chunks(args.input, by="heading", max_chars=4000)
    pattern = re.compile(args.pattern)
    all_paras = list(root.iter(f"{{{WNS}}}p"))

    results: list[dict] = []
    for chunk in chunks_meta:
        start = chunk["start_para"]
        end = chunk.get("end_para", len(all_paras) - 1)
        for pi in range(start, min(end + 1, len(all_paras))):
            text = _get_para_text(all_paras[pi])
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


def cmd_comment(args: argparse.Namespace) -> int:
    """Add comments to DOCX."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from comment import add_comments

    if args.json_file:
        with open(args.json_file, encoding="utf-8") as f:
            comments_list = json.load(f)
    else:
        if not args.anchor:
            print("Error: --anchor is required when using --text", file=sys.stderr)
            return 1
        comments_list = [{"author": args.author, "text": args.text, "anchor": args.anchor}]

    msg = add_comments(args.input, args.output, comments_list)
    print(msg)
    return 1 if msg.startswith("Error") else 0


def cmd_accept_changes(args: argparse.Namespace) -> int:
    """Accept all tracked changes."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from accept_changes import accept_changes
    msg = accept_changes(args.input, args.output)
    print(msg)
    return 1 if msg.startswith("Error") else 0


def cmd_merge_runs(args: argparse.Namespace) -> int:
    """Merge adjacent runs with identical formatting."""
    sys.path.insert(0, str(SCRIPT_DIR))
    from ooxml.merge_runs import merge_adjacent_runs
    result = merge_adjacent_runs(args.path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Merged {result['merged_count']} run(s) in {result['files_modified']} file(s)")
        if result["proof_errors_removed"]:
            print(f"Removed {result['proof_errors_removed']} proofErr element(s)")
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified CLI for DOCX document operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # open
    p = sub.add_parser("open", help="Unpack DOCX to directory with pretty-printed XML")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("output_dir", help="Output directory")

    # save
    p = sub.add_parser("save", help="Pack directory to DOCX")
    p.add_argument("input_dir", help="Input directory")
    p.add_argument("output", help="Output .docx file")

    # validate
    p = sub.add_parser("validate", help="Structural validation")
    p.add_argument("input", help="Input .docx file or unpacked directory")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # repair
    p = sub.add_parser("repair", help="Auto-repair (dry-run by default)")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("--apply", action="store_true", help="Apply repairs (default: dry-run)")
    p.add_argument("-o", "--output", help="Output file (implies --apply)")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # text
    p = sub.add_parser("text", help="Extract text from DOCX")
    p.add_argument("input", help="Input .docx file")

    # search
    p = sub.add_parser("search", help="Search text content with regex")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("pattern", help="Regex pattern to search")

    # toc
    p = sub.add_parser("toc", help="Extract heading-based table of contents")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # chunk
    p = sub.add_parser("chunk", help="Split document into chunks for agentic reading")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("--by", choices=["heading", "size"], default="heading",
                   help="Chunking strategy (default: heading)")
    p.add_argument("--max-chars", type=int, default=4000,
                   help="Max chars per chunk in size mode (default: 4000)")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # search-chunks
    p = sub.add_parser("search-chunks", help="Search within heading-based chunks")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("pattern", help="Regex pattern to search")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    # comment
    p = sub.add_parser("comment", help="Add comments to DOCX")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("output", help="Output .docx file")
    comment_group = p.add_mutually_exclusive_group(required=True)
    comment_group.add_argument("--json", dest="json_file", help="JSON file with comments array")
    comment_group.add_argument("--text", help="Comment text")
    p.add_argument("--author", default="Agent", help="Comment author (default: Agent)")
    p.add_argument("--anchor", help="Text to attach the comment to")

    # accept-changes
    p = sub.add_parser("accept-changes", help="Accept all tracked changes")
    p.add_argument("input", help="Input .docx file")
    p.add_argument("output", help="Output .docx file")

    # merge-runs
    p = sub.add_parser("merge-runs", help="Merge adjacent runs with identical formatting")
    p.add_argument("path", help="Unpacked DOCX directory")
    p.add_argument("--json", "-j", action="store_true", help="JSON output")

    args = parser.parse_args()

    commands = {
        "open": cmd_open,
        "save": cmd_save,
        "validate": cmd_validate,
        "repair": cmd_repair,
        "text": cmd_text,
        "search": cmd_search,
        "toc": cmd_toc,
        "chunk": cmd_chunk,
        "search-chunks": cmd_search_chunks,
        "comment": cmd_comment,
        "accept-changes": cmd_accept_changes,
        "merge-runs": cmd_merge_runs,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
