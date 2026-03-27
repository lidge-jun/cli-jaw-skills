#!/usr/bin/env python3
"""Build and verify PPTX regression fixtures."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_DIR = Path(__file__).resolve().parent / "expected"
METADATA_DIR = Path(__file__).resolve().parent / "metadata"

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
PKG_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _slide_xml(texts: list[str]) -> str:
    shapes = ""
    for i, text in enumerate(texts, 1):
        shapes += f"""
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="{i}" name="TextBox {i}"/>
          <p:cNvSpPr txBox="1"/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm xmlns:a="{A}">
            <a:off x="0" y="0"/>
            <a:ext cx="9144000" cy="1000000"/>
          </a:xfrm>
        </p:spPr>
        <p:txBody>
          <a:bodyPr xmlns:a="{A}"/>
          <a:p xmlns:a="{A}">
            <a:r><a:t>{text}</a:t></a:r>
          </a:p>
        </p:txBody>
      </p:sp>"""
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="0" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr/>
      {shapes}
    </p:spTree>
  </p:cSld>
</p:sld>"""


def _make_minimal_pptx(slide_texts: list[list[str]]) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        ct_overrides = []
        pres_slides = []
        pres_rels = []
        for i, texts in enumerate(slide_texts, 1):
            ct_overrides.append(
                f'  <Override PartName="/ppt/slides/slide{i}.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            )
            pres_slides.append(f'    <p:sldId id="{255 + i}" r:id="rId{i}"/>')
            pres_rels.append(
                f'  <Relationship Id="rId{i}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
                f'Target="slides/slide{i}.xml"/>'
            )

        zf.writestr("[Content_Types].xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT_NS}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
{chr(10).join(ct_overrides)}
</Types>""")
        zf.writestr("_rels/.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""")
        zf.writestr("ppt/presentation.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="{P}" xmlns:r="{R}" xmlns:a="{A}">
  <p:sldMasterIdLst/>
  <p:sldIdLst>
{chr(10).join(pres_slides)}
  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""")
        zf.writestr("ppt/_rels/presentation.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
{chr(10).join(pres_rels)}
</Relationships>""")
        for i, texts in enumerate(slide_texts, 1):
            zf.writestr(f"ppt/slides/slide{i}.xml", _slide_xml(texts))
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}"/>""")
    buf.seek(0)
    return buf


def _rewrite_zip(src_path: Path, out_path: Path, replacements: dict[str, str], extra_parts: dict[str, bytes | str] | None = None) -> None:
    extra_parts = extra_parts or {}
    with zipfile.ZipFile(src_path, "r") as src, zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            if item in replacements:
                dst.writestr(item, replacements[item])
            else:
                dst.writestr(item, src.read(item))
        for item, data in extra_parts.items():
            dst.writestr(item, data)


def create_basic_slides() -> None:
    out = FIXTURES_DIR / "basic_slides.pptx"
    out.write_bytes(_make_minimal_pptx([
        ["Title Slide", "Subtitle text"],
        ["Second Slide", "Content paragraph one", "Content paragraph two"],
        ["Third Slide", "Final content"],
    ]).read())


def create_orphan_media() -> None:
    tmp = FIXTURES_DIR / "_tmp_orphan_source.pptx"
    tmp.write_bytes(_make_minimal_pptx([["Slide with no media references"]]).read())
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    out = FIXTURES_DIR / "orphan_media.pptx"
    with zipfile.ZipFile(tmp, "r") as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            data = src.read(item)
            if item == "[Content_Types].xml":
                text = data.decode("utf-8")
                text = text.replace("</Types>", '  <Default Extension="png" ContentType="image/png"/>\n</Types>')
                dst.writestr(item, text)
            else:
                dst.writestr(item, data)
        dst.writestr("ppt/media/orphan_image.png", png_data)
    tmp.unlink()


def create_broken_layout() -> None:
    tmp = FIXTURES_DIR / "_tmp_broken_layout_source.pptx"
    tmp.write_bytes(_make_minimal_pptx([["Slide referencing missing layout"]]).read())
    out = FIXTURES_DIR / "broken_layout.pptx"
    broken_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout99.xml"/>
</Relationships>"""
    _rewrite_zip(tmp, out, {"ppt/slides/_rels/slide1.xml.rels": broken_rels})
    tmp.unlink()


def create_blankless_minimal_deck() -> None:
    out = FIXTURES_DIR / "blankless_minimal_deck.pptx"
    out.write_bytes(_make_minimal_pptx([["Blankless minimal"]]).read())


def create_blank_layout_named_nonstandard() -> None:
    base = FIXTURES_DIR / "_tmp_blank_named_source.pptx"
    base.write_bytes(_make_minimal_pptx([["Layout-backed slide"]]).read())
    replacements = {
        "[Content_Types].xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT_NS}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>""",
        "ppt/presentation.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="{P}" xmlns:r="{R}" xmlns:a="{A}">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId2"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId1"/>
  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""",
        "ppt/_rels/presentation.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
</Relationships>""",
        "ppt/slides/_rels/slide1.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>""",
    }
    extra_parts = {
        "ppt/slideLayouts/slideLayout1.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="{P}" xmlns:a="{A}" type="blank">
  <p:cSld name="NotActuallyBlankName">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="0" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr/>
    </p:spTree>
  </p:cSld>
</p:sldLayout>""",
        "ppt/slideLayouts/_rels/slideLayout1.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>""",
        "ppt/slideMasters/slideMaster1.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="0" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>""",
        "ppt/slideMasters/_rels/slideMaster1.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>""",
    }
    out = FIXTURES_DIR / "blank_layout_named_nonstandard.pptx"
    _rewrite_zip(base, out, replacements, extra_parts)
    base.unlink()


def create_duplicate_media_chart_deck() -> None:
    base = FIXTURES_DIR / "_tmp_duplicate_media_source.pptx"
    base.write_bytes(_make_minimal_pptx([["Media chart source"]]).read())
    replacements = {
        "[Content_Types].xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT_NS}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
  <Override PartName="/ppt/charts/chart1.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>
</Types>""",
        "ppt/slides/_rels/slide1.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/image1.png"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart" Target="../charts/chart1.xml"/>
</Relationships>""",
    }
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
        b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    chart_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<c:chartSpace xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart">
  <c:chart><c:title/></c:chart>
</c:chartSpace>"""
    out = FIXTURES_DIR / "duplicate_media_chart_deck.pptx"
    _rewrite_zip(base, out, replacements, {"ppt/media/image1.png": png_data, "ppt/charts/chart1.xml": chart_xml})
    base.unlink()
    meta = {
        "fixture": out.name,
        "sha256": _sha256(out),
        "must_exist": [
            "ppt/slides/slide1.xml",
            "ppt/slides/_rels/slide1.xml.rels",
            "ppt/media/image1.png",
            "ppt/charts/chart1.xml",
        ],
        "xml_assertions": [
            {"path": "ppt/slides/_rels/slide1.xml.rels", "contains": "relationships/chart"},
            {"path": "ppt/slides/_rels/slide1.xml.rels", "contains": "relationships/image"},
        ],
    }
    (METADATA_DIR / "duplicate_media_chart_deck.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def create_notes_reuse_conflict() -> None:
    base = FIXTURES_DIR / "_tmp_notes_conflict_source.pptx"
    base.write_bytes(_make_minimal_pptx([["Slide one"], ["Slide two"]]).read())
    replacements = {
        "ppt/slides/_rels/slide1.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide1.xml"/>
</Relationships>""",
        "ppt/slides/_rels/slide2.xml.rels": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide1.xml"/>
</Relationships>""",
    }
    notes_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:notes xmlns:p="{P}" xmlns:a="{A}">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="0" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:notes>"""
    out = FIXTURES_DIR / "notes_reuse_conflict.pptx"
    _rewrite_zip(base, out, replacements, {"ppt/notesSlides/notesSlide1.xml": notes_xml})
    base.unlink()
    meta = {
        "fixture": out.name,
        "sha256": _sha256(out),
        "must_exist": [
            "ppt/slides/slide1.xml",
            "ppt/slides/slide2.xml",
            "ppt/notesSlides/notesSlide1.xml",
        ],
        "xml_assertions": [
            {"path": "ppt/slides/_rels/slide1.xml.rels", "contains": "relationships/notesSlide"},
            {"path": "ppt/slides/_rels/slide2.xml.rels", "contains": "relationships/notesSlide"},
        ],
    }
    (METADATA_DIR / "notes_reuse_conflict.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _validate_json(path: Path) -> dict:
    sys.path.insert(0, str((Path(__file__).resolve().parent.parent / "scripts" / "ooxml").parent))
    from ooxml.validate import validate

    return validate(str(path))


def _summary_duplicate_media_chart(path: Path) -> dict:
    with zipfile.ZipFile(path, "r") as zf:
        rels = zf.read("ppt/slides/_rels/slide1.xml.rels").decode("utf-8")
    return {
        "has_chart_rel": "relationships/chart" in rels,
        "has_image_rel": "relationships/image" in rels,
    }


def _write_expected_files() -> None:
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
    (EXPECTED_DIR / "validate_blankless_minimal_deck.json").write_text(
        json.dumps(_validate_json(FIXTURES_DIR / "blankless_minimal_deck.pptx"), indent=2), encoding="utf-8"
    )
    (EXPECTED_DIR / "validate_blank_layout_named_nonstandard.json").write_text(
        json.dumps(_validate_json(FIXTURES_DIR / "blank_layout_named_nonstandard.pptx"), indent=2), encoding="utf-8"
    )
    (EXPECTED_DIR / "duplicate_media_chart_summary.json").write_text(
        json.dumps(_summary_duplicate_media_chart(FIXTURES_DIR / "duplicate_media_chart_deck.pptx"), indent=2), encoding="utf-8"
    )
    (EXPECTED_DIR / "notes_reuse_conflict.json").write_text(
        json.dumps(_validate_json(FIXTURES_DIR / "notes_reuse_conflict.pptx"), indent=2), encoding="utf-8"
    )


def _verify_metadata(meta_path: Path) -> tuple[bool, dict]:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    fixture = FIXTURES_DIR / meta["fixture"]
    result = {"fixture": meta["fixture"], "exists": fixture.exists(), "checksum_ok": False, "assertions_ok": False}
    if not fixture.exists():
        return False, result
    result["checksum_ok"] = _sha256(fixture) == meta["sha256"]
    with zipfile.ZipFile(fixture, "r") as zf:
        missing = [name for name in meta["must_exist"] if name not in zf.namelist()]
        assertions_ok = not missing
        for assertion in meta["xml_assertions"]:
            text = zf.read(assertion["path"]).decode("utf-8")
            if assertion["contains"] not in text:
                assertions_ok = False
        result["assertions_ok"] = assertions_ok
    return result["checksum_ok"] and result["assertions_ok"], result


def build(only: str | None = None, force: bool = False) -> list[dict]:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    registry = {
        "basic_slides": create_basic_slides,
        "orphan_media": create_orphan_media,
        "broken_layout": create_broken_layout,
        "blankless_minimal_deck": create_blankless_minimal_deck,
        "blank_layout_named_nonstandard": create_blank_layout_named_nonstandard,
        "duplicate_media_chart_deck": create_duplicate_media_chart_deck,
        "notes_reuse_conflict": create_notes_reuse_conflict,
    }
    results = []
    for name, fn in registry.items():
        if only and only != name:
            continue
        suffix = ".pptx"
        target = FIXTURES_DIR / f"{name}{suffix}"
        if target.exists() and not force:
            results.append({"fixture": target.name, "status": "SKIPPED"})
            continue
        fn()
        results.append({"fixture": target.name, "status": "CREATED", "sha256": _sha256(target)})
    if not only:
        _write_expected_files()
    return results


def verify(only: str | None = None) -> dict:
    mapping = {
        "basic_slides": {"fixture": "basic_slides.pptx"},
        "orphan_media": {"fixture": "orphan_media.pptx"},
        "broken_layout": {"fixture": "broken_layout.pptx"},
        "blankless_minimal_deck": {"fixture": "blankless_minimal_deck.pptx"},
        "blank_layout_named_nonstandard": {"fixture": "blank_layout_named_nonstandard.pptx"},
    }
    checked = []
    failed = []
    details = []
    for slug, cfg in mapping.items():
        if only and only != slug:
            continue
        fixture = FIXTURES_DIR / cfg["fixture"]
        result = {"fixture": cfg["fixture"], "exists": fixture.exists(), "checksum_ok": fixture.exists(), "assertions_ok": fixture.exists()}
        if not fixture.exists():
            failed.append(slug)
        checked.append(slug)
        details.append(result)

    for meta_name in ("duplicate_media_chart_deck.meta.json", "notes_reuse_conflict.meta.json"):
        slug = meta_name.replace(".meta.json", "")
        if only and only != slug:
            continue
        ok, result = _verify_metadata(METADATA_DIR / meta_name)
        checked.append(slug)
        details.append(result)
        if not ok:
            failed.append(slug)
    return {"mode": "verify", "skill": "pptx", "ok": not failed, "checked": checked, "failed": failed, "details": details}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify PPTX regression fixtures")
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--only")
    build_parser.add_argument("--force", action="store_true")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--only")
    verify_parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.command == "build":
        results = build(only=args.only, force=args.force)
        for item in results:
            print(f"{item['status']} {item['fixture']}")
        return 0

    result = verify(only=args.only)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for detail in result["details"]:
            if detail["exists"] and detail["checksum_ok"] and detail["assertions_ok"]:
                print(f"VERIFIED {detail['fixture']}")
            else:
                print(f"FAILED {detail['fixture']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
