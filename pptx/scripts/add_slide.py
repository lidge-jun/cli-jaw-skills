"""Add or duplicate slides in an unpacked PPTX directory.

Works on the unpacked OOXML structure (run unpack.py first).
Can add a blank slide or duplicate an existing one.

Usage:
    python add_slide.py <unpacked_dir> --blank
    python add_slide.py <unpacked_dir> --duplicate <slide_number>
    python add_slide.py <unpacked_dir> --duplicate 3 --position 1
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

import defusedxml.minidom


def add_blank_slide(unpacked_dir: str, position: int | None = None) -> str:
    """Add a blank slide to the unpacked PPTX."""
    root = Path(unpacked_dir)
    slides_dir = root / "ppt" / "slides"

    if not slides_dir.is_dir():
        return f"Error: {slides_dir} not found — is this an unpacked PPTX?"

    next_num = _get_next_slide_number(slides_dir)

    # Create minimal slide XML
    slide_xml = _create_blank_slide_xml()
    slide_path = slides_dir / f"slide{next_num}.xml"
    slide_path.write_text(slide_xml, encoding="utf-8")

    # Create rels file
    rels_dir = slides_dir / "_rels"
    rels_dir.mkdir(exist_ok=True)
    rels_path = rels_dir / f"slide{next_num}.xml.rels"
    rels_path.write_text(_create_slide_rels_xml(root, prefer_blank=True), encoding="utf-8")

    # Update presentation.xml
    _register_slide(root, next_num, position)

    # Update [Content_Types].xml
    _add_content_type(root, next_num)

    return f"Added blank slide{next_num}.xml (position: {position or 'end'})"


def duplicate_slide(unpacked_dir: str, source_num: int, position: int | None = None) -> str:
    """Duplicate an existing slide."""
    root = Path(unpacked_dir)
    slides_dir = root / "ppt" / "slides"
    source_path = slides_dir / f"slide{source_num}.xml"

    if not source_path.exists():
        return f"Error: slide{source_num}.xml not found"

    next_num = _get_next_slide_number(slides_dir)

    # Copy slide XML
    dest_path = slides_dir / f"slide{next_num}.xml"
    shutil.copy2(source_path, dest_path)

    # Copy rels if exists, otherwise create from source's layout
    source_rels = slides_dir / "_rels" / f"slide{source_num}.xml.rels"
    if source_rels.exists():
        dest_rels = slides_dir / "_rels" / f"slide{next_num}.xml.rels"
        shutil.copy2(source_rels, dest_rels)
    else:
        rels_dir = slides_dir / "_rels"
        rels_dir.mkdir(exist_ok=True)
        dest_rels = rels_dir / f"slide{next_num}.xml.rels"
        dest_rels.write_text(
            _create_slide_rels_xml(root, prefer_blank=False), encoding="utf-8"
        )

    # Update presentation.xml
    _register_slide(root, next_num, position)

    # Update [Content_Types].xml
    _add_content_type(root, next_num)

    return f"Duplicated slide{source_num} → slide{next_num}.xml (position: {position or 'end'})"


def _get_next_slide_number(slides_dir: Path) -> int:
    """Find the next available slide number."""
    existing = [
        int(m.group(1))
        for f in slides_dir.glob("slide*.xml")
        if (m := re.match(r"slide(\d+)\.xml", f.name))
    ]
    return max(existing, default=0) + 1


def _create_blank_slide_xml() -> str:
    """Generate minimal blank slide XML."""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
        ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
        "  <p:cSld>\n"
        "    <p:spTree>\n"
        '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
        "<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n"
        "      <p:grpSpPr/>\n"
        "    </p:spTree>\n"
        "  </p:cSld>\n"
        "</p:sld>"
    )


# ---------------------------------------------------------------------------
# Layout detection helpers
# ---------------------------------------------------------------------------

_BLANK_NAMES = {"blank", "빈 화면", "空白", "leer", "vide", "vacío", "vuota"}
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _find_blank_layout(root: Path) -> str:
    """Find a visually blank slide layout.

    Strategy priority:
    1. Match by p:cSld name attribute (Blank/빈 화면/空白/Leer/Vide)
    2. Empty spTree (structurally blank regardless of name)
    3. Any layout with valid slideMaster relationship
    4. Fallback to slideLayout1.xml
    """
    layouts_dir = root / "ppt" / "slideLayouts"
    if not layouts_dir.is_dir():
        return ""

    # Strategy 1: Match by name
    for layout_path in sorted(layouts_dir.glob("slideLayout*.xml")):
        try:
            dom = defusedxml.minidom.parseString(layout_path.read_bytes())
            for csld in dom.getElementsByTagNameNS(P_NS, "cSld"):
                name = (csld.getAttribute("name") or "").strip().lower()
                if name in _BLANK_NAMES:
                    return f"../slideLayouts/{layout_path.name}"
        except Exception:
            continue

    # Strategy 2: Find layout with empty shape tree
    for layout_path in sorted(layouts_dir.glob("slideLayout*.xml")):
        try:
            dom = defusedxml.minidom.parseString(layout_path.read_bytes())
            sp_trees = dom.getElementsByTagNameNS(P_NS, "spTree")
            if sp_trees:
                sp_tree = sp_trees[0]
                shape_count = sum(
                    1
                    for c in sp_tree.childNodes
                    if getattr(c, "localName", None)
                    not in (None, "nvGrpSpPr", "grpSpPr")
                )
                if shape_count == 0:
                    return f"../slideLayouts/{layout_path.name}"
        except Exception:
            continue

    # Strategy 3: Any layout with valid slideMaster relationship
    rels_dir = layouts_dir / "_rels"
    for layout_path in sorted(layouts_dir.glob("slideLayout*.xml")):
        rels_file = rels_dir / f"{layout_path.name}.rels"
        if rels_file.exists():
            try:
                dom = defusedxml.minidom.parseString(rels_file.read_bytes())
                for rel in dom.getElementsByTagName("Relationship"):
                    if "slideMaster" in rel.getAttribute("Type"):
                        return f"../slideLayouts/{layout_path.name}"
            except Exception:
                continue

    # Strategy 4: Fallback
    return ""


def _find_source_layout(root: Path) -> str | None:
    """Reuse slide1's layout relationship (for --duplicate)."""
    slide1_rels = root / "ppt" / "slides" / "_rels" / "slide1.xml.rels"
    if not slide1_rels.exists():
        return None
    try:
        dom = defusedxml.minidom.parseString(slide1_rels.read_bytes())
        for rel in dom.getElementsByTagName("Relationship"):
            if "slideLayout" in rel.getAttribute("Type"):
                return rel.getAttribute("Target")
    except Exception:
        pass
    return None


def _create_slide_rels_xml(root: Path, *, prefer_blank: bool = True) -> str:
    """Create slide rels pointing to a compatible layout.

    Args:
        root: Unpacked PPTX root directory.
        prefer_blank: If True, prioritize blank layouts (for --blank).
                      If False, clone slide1's layout (for --duplicate).
    """
    if prefer_blank:
        layout_target = _find_blank_layout(root)
    else:
        layout_target = _find_source_layout(root) or _find_blank_layout(root)

    if not layout_target:
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            "</Relationships>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f'  <Relationship Id="rId1"'
        f' Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"'
        f' Target="{layout_target}"/>\n'
        "</Relationships>"
    )


def _register_slide(root: Path, slide_num: int, position: int | None) -> None:
    """Add slide reference to presentation.xml."""
    pres_path = root / "ppt" / "presentation.xml"
    if not pres_path.exists():
        return

    dom = defusedxml.minidom.parseString(pres_path.read_bytes())

    # Find p:sldIdLst
    sld_lists = dom.getElementsByTagNameNS(
        "http://schemas.openxmlformats.org/presentationml/2006/main", "sldIdLst"
    )
    if not sld_lists:
        return

    sld_list = sld_lists[0]

    # Get max ID
    max_id = 255
    for sld_id in sld_list.childNodes:
        if hasattr(sld_id, "getAttribute"):
            current_id = sld_id.getAttribute("id")
            if current_id:
                max_id = max(max_id, int(current_id))

    # Add relationship to presentation rels
    _add_pres_rel(root, slide_num)

    # Create new sldId element
    new_sld = dom.createElementNS(
        "http://schemas.openxmlformats.org/presentationml/2006/main", "p:sldId"
    )
    new_sld.setAttribute("id", str(max_id + 1))

    # Find the rId we just added
    rel_id = _get_slide_rel_id(root, slide_num)
    if rel_id:
        new_sld.setAttributeNS(
            "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
            "r:id",
            rel_id,
        )

    if position and position <= len(list(sld_list.childNodes)):
        children = [c for c in sld_list.childNodes if hasattr(c, "getAttribute")]
        if position - 1 < len(children):
            sld_list.insertBefore(new_sld, children[position - 1])
        else:
            sld_list.appendChild(new_sld)
    else:
        sld_list.appendChild(new_sld)

    pres_path.write_bytes(dom.toxml(encoding="UTF-8"))


def _add_pres_rel(root: Path, slide_num: int) -> None:
    """Add slide relationship to presentation.xml.rels."""
    rels_path = root / "ppt" / "_rels" / "presentation.xml.rels"
    if not rels_path.exists():
        return

    dom = defusedxml.minidom.parseString(rels_path.read_bytes())
    rels_root = dom.documentElement

    # Find max rId number
    max_rid = 0
    for rel in rels_root.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        m = re.match(r"rId(\d+)", rid)
        if m:
            max_rid = max(max_rid, int(m.group(1)))

    new_rel = dom.createElement("Relationship")
    new_rel.setAttribute("Id", f"rId{max_rid + 1}")
    new_rel.setAttribute(
        "Type",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide",
    )
    new_rel.setAttribute("Target", f"slides/slide{slide_num}.xml")
    rels_root.appendChild(new_rel)

    rels_path.write_bytes(dom.toxml(encoding="UTF-8"))


def _get_slide_rel_id(root: Path, slide_num: int) -> str | None:
    """Get the relationship ID for a slide."""
    rels_path = root / "ppt" / "_rels" / "presentation.xml.rels"
    if not rels_path.exists():
        return None

    dom = defusedxml.minidom.parseString(rels_path.read_bytes())
    target = f"slides/slide{slide_num}.xml"

    for rel in dom.getElementsByTagName("Relationship"):
        if rel.getAttribute("Target") == target:
            return rel.getAttribute("Id")
    return None


def _add_content_type(root: Path, slide_num: int) -> None:
    """Add content type entry for the new slide."""
    ct_path = root / "[Content_Types].xml"
    if not ct_path.exists():
        return

    dom = defusedxml.minidom.parseString(ct_path.read_bytes())
    ct_root = dom.documentElement

    override = dom.createElement("Override")
    override.setAttribute("PartName", f"/ppt/slides/slide{slide_num}.xml")
    override.setAttribute(
        "ContentType",
        "application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
    )
    ct_root.appendChild(override)

    ct_path.write_bytes(dom.toxml(encoding="UTF-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add or duplicate slides in unpacked PPTX")
    parser.add_argument("unpacked_dir", help="Path to unpacked PPTX directory")
    parser.add_argument("--position", type=int, help="Insert position (1-based)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--blank", action="store_true", help="Add a blank slide")
    group.add_argument("--duplicate", type=int, metavar="N", help="Duplicate slide N")

    args = parser.parse_args()

    if args.blank:
        msg = add_blank_slide(args.unpacked_dir, position=args.position)
    else:
        msg = duplicate_slide(args.unpacked_dir, args.duplicate, position=args.position)

    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
