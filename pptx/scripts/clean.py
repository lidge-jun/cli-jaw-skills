"""Remove orphaned files from an unpacked PPTX.

Scans the PPTX structure for unreferenced media, layouts, and other parts,
then optionally removes them to reduce file size.

Usage:
    python clean.py <unpacked_dir>            # Dry run — shows orphans
    python clean.py <unpacked_dir> --delete   # Actually remove orphaned files
"""

import argparse
import re
import sys
from pathlib import Path

import defusedxml.minidom


def find_orphans(unpacked_dir: str) -> list[Path]:
    """Find files not referenced by any relationship."""
    root = Path(unpacked_dir)

    if not (root / "ppt").is_dir():
        print(f"Error: {unpacked_dir} does not look like an unpacked PPTX", file=sys.stderr)
        return []

    # Collect all referenced targets from all .rels files
    referenced = set()
    for rels_file in root.rglob("*.rels"):
        try:
            dom = defusedxml.minidom.parseString(rels_file.read_bytes())
            rels_dir = rels_file.parent.parent
            for rel in dom.getElementsByTagName("Relationship"):
                target = rel.getAttribute("Target")
                if not target or target.startswith("http://") or target.startswith("https://"):
                    continue
                resolved = (rels_dir / target).resolve()
                referenced.add(resolved)
        except Exception:
            continue

    # Collect all referenced targets from [Content_Types].xml
    ct_path = root / "[Content_Types].xml"
    if ct_path.exists():
        try:
            dom = defusedxml.minidom.parseString(ct_path.read_bytes())
            for override in dom.getElementsByTagName("Override"):
                part = override.getAttribute("PartName")
                if part:
                    # PartName starts with /
                    resolved = (root / part.lstrip("/")).resolve()
                    referenced.add(resolved)
        except Exception:
            pass

    # Also always keep essential files
    essential = {
        (root / "[Content_Types].xml").resolve(),
        (root / "_rels" / ".rels").resolve(),
        (root / "ppt" / "presentation.xml").resolve(),
    }
    referenced.update(essential)

    # Keep all .rels files (they're structural)
    for rels_file in root.rglob("*.rels"):
        referenced.add(rels_file.resolve())

    # Find orphans in media/ directory
    orphans = []
    media_dir = root / "ppt" / "media"
    if media_dir.is_dir():
        for media_file in media_dir.iterdir():
            if media_file.is_file() and media_file.resolve() not in referenced:
                orphans.append(media_file)

    # Find orphaned slide layouts
    layouts_dir = root / "ppt" / "slideLayouts"
    if layouts_dir.is_dir():
        for layout_file in layouts_dir.glob("slideLayout*.xml"):
            if layout_file.resolve() not in referenced:
                orphans.append(layout_file)

    return sorted(orphans)


def clean(unpacked_dir: str, delete: bool = False) -> str:
    """Find and optionally remove orphaned files."""
    orphans = find_orphans(unpacked_dir)

    if not orphans:
        return "No orphaned files found."

    root = Path(unpacked_dir)
    lines = [f"Found {len(orphans)} orphaned file(s):"]

    total_size = 0
    for orphan in orphans:
        size = orphan.stat().st_size
        total_size += size
        rel = orphan.relative_to(root)
        lines.append(f"  {'DELETED' if delete else '  '} {rel} ({_fmt_size(size)})")

        if delete:
            orphan.unlink()

    lines.append(f"\nTotal: {_fmt_size(total_size)}")

    if not delete:
        lines.append("\nRun with --delete to remove these files.")

    return "\n".join(lines)


def _fmt_size(size: int) -> str:
    """Format byte size for display."""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove orphaned files from unpacked PPTX")
    parser.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    parser.add_argument("--delete", action="store_true", help="Actually delete orphaned files")
    args = parser.parse_args()

    result = clean(args.unpacked_dir, delete=args.delete)
    print(result)
