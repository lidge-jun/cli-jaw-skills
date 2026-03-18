#!/usr/bin/env python3
"""Generate PPTX test fixture files.

Creates minimal PPTX files for regression testing:
    fixtures/basic_slides.pptx     — Simple 3-slide deck with text
    fixtures/orphan_media.pptx     — PPTX with unreferenced media file
    fixtures/broken_layout.pptx    — PPTX with missing layout reference
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Namespaces
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
PKG_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def _slide_xml(texts: list[str]) -> str:
    """Create a minimal slide XML with text boxes."""
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


def _make_minimal_pptx(num_slides: int = 1, slide_texts: list[list[str]] | None = None) -> io.BytesIO:
    """Create a minimal valid PPTX in memory."""
    if slide_texts is None:
        slide_texts = [[f"Slide {i+1}"] for i in range(num_slides)]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Build slide list entries
        ct_overrides = ""
        pres_slides = ""
        pres_rels = ""
        for i in range(1, len(slide_texts) + 1):
            ct_overrides += f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
            pres_slides += f'    <p:sldId id="{255 + i}" r:id="rId{i}"/>\n'
            pres_rels += f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n'

        # [Content_Types].xml
        zf.writestr("[Content_Types].xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT_NS}">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
{ct_overrides}</Types>""")

        # _rels/.rels
        zf.writestr("_rels/.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""")

        # ppt/presentation.xml
        zf.writestr("ppt/presentation.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="{P}" xmlns:r="{R}" xmlns:a="{A}">
  <p:sldMasterIdLst/>
  <p:sldIdLst>
{pres_slides}  </p:sldIdLst>
  <p:sldSz cx="9144000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>""")

        # ppt/_rels/presentation.xml.rels
        zf.writestr("ppt/_rels/presentation.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
{pres_rels}</Relationships>""")

        # Slide files
        for i, texts in enumerate(slide_texts, 1):
            zf.writestr(f"ppt/slides/slide{i}.xml", _slide_xml(texts))
            zf.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}"/>""")

    buf.seek(0)
    return buf


def create_basic_slides():
    """Simple 3-slide deck with text."""
    slide_texts = [
        ["Title Slide", "Subtitle text"],
        ["Second Slide", "Content paragraph one", "Content paragraph two"],
        ["Third Slide", "Final content"],
    ]
    out = FIXTURES_DIR / "basic_slides.pptx"
    buf = _make_minimal_pptx(slide_texts=slide_texts)
    out.write_bytes(buf.read())
    print(f"  Created: {out.name}")


def create_orphan_media():
    """PPTX with an unreferenced media file in ppt/media/."""
    slide_texts = [["Slide with no media references"]]
    buf = _make_minimal_pptx(slide_texts=slide_texts)

    out = FIXTURES_DIR / "orphan_media.pptx"
    with zipfile.ZipFile(buf, "r") as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            dst.writestr(item, src.read(item))
        # Add orphan image (1x1 red pixel PNG)
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
            b'\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00'
            b'\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        dst.writestr("ppt/media/orphan_image.png", png_data)
        # Update Content_Types to include png
        ct = src.read("[Content_Types].xml").decode("utf-8")
        ct = ct.replace("</Types>",
            '  <Default Extension="png" ContentType="image/png"/>\n</Types>')
        # Re-write Content_Types (already written above, so we need to use a fresh zip)

    # Rebuild to add Content_Types with png extension
    buf2 = io.BytesIO()
    with zipfile.ZipFile(out, "r") as src2, zipfile.ZipFile(buf2, "w", zipfile.ZIP_DEFLATED) as dst2:
        for item in src2.namelist():
            data = src2.read(item)
            if item == "[Content_Types].xml":
                text = data.decode("utf-8")
                if "image/png" not in text:
                    text = text.replace("</Types>",
                        '  <Default Extension="png" ContentType="image/png"/>\n</Types>')
                dst2.writestr(item, text)
            else:
                dst2.writestr(item, data)
    buf2.seek(0)
    out.write_bytes(buf2.read())
    print(f"  Created: {out.name}")


def create_broken_layout():
    """PPTX where a slide .rels references a non-existent layout."""
    slide_texts = [["Slide referencing missing layout"]]
    buf = _make_minimal_pptx(slide_texts=slide_texts)

    out = FIXTURES_DIR / "broken_layout.pptx"
    with zipfile.ZipFile(buf, "r") as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            if item == "ppt/slides/_rels/slide1.xml.rels":
                # Point to non-existent layout
                broken_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{PKG_RELS}">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout99.xml"/>
</Relationships>"""
                dst.writestr(item, broken_rels)
            else:
                dst.writestr(item, src.read(item))
    print(f"  Created: {out.name}")


def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating PPTX fixtures...")
    create_basic_slides()
    create_orphan_media()
    create_broken_layout()
    print("Done.")


if __name__ == "__main__":
    main()
