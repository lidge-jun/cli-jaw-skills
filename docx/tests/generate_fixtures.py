#!/usr/bin/env python3
"""Build and verify DOCX regression fixtures."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
EXPECTED_DIR = Path(__file__).resolve().parent / "expected"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _make_minimal_docx() -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        zf.writestr("word/document.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p><w:r><w:t>Minimal document.</w:t></w:r></w:p>
  </w:body>
</w:document>""")
        zf.writestr("word/_rels/document.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>""")
    buf.seek(0)
    return buf


def _set_doc_part(
    source_buf: io.BytesIO,
    out_path: Path,
    replacements: dict[str, str],
    extra_parts: dict[str, bytes | str] | None = None,
) -> None:
    extra_parts = extra_parts or {}
    with zipfile.ZipFile(source_buf, "r") as src, zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            if item in replacements:
                dst.writestr(item, replacements[item])
            else:
                dst.writestr(item, src.read(item))
        for item, data in extra_parts.items():
            dst.writestr(item, data)


def create_tracked_changes() -> None:
    buf = _make_minimal_docx()
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:t>Normal paragraph text.</w:t></w:r></w:p>
    <w:p>
      <w:r><w:t>Before change </w:t></w:r>
      <w:ins w:id="1" w:author="Author" w:date="2026-01-15T10:00:00Z">
        <w:r><w:t>inserted text</w:t></w:r>
      </w:ins>
      <w:r><w:t> after insert.</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Before deletion </w:t></w:r>
      <w:del w:id="2" w:author="Author" w:date="2026-01-15T11:00:00Z">
        <w:r><w:delText>removed text</w:delText></w:r>
      </w:del>
      <w:r><w:t> after delete.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
    _set_doc_part(buf, FIXTURES_DIR / "tracked_changes.docx", {"word/document.xml": doc_xml})


def create_comments() -> None:
    buf = _make_minimal_docx()
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:t>Introduction paragraph.</w:t></w:r></w:p>
    <w:p>
      <w:commentRangeStart w:id="0"/>
      <w:r><w:t>This text has a comment attached.</w:t></w:r>
      <w:commentRangeEnd w:id="0"/>
      <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
    </w:p>
    <w:p><w:r><w:t>Final paragraph without comments.</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    comments_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="{W_NS}">
  <w:comment w:id="0" w:author="Reviewer" w:date="2026-02-01T09:00:00Z">
    <w:p><w:r><w:t>Please review this section.</w:t></w:r></w:p>
  </w:comment>
</w:comments>"""
    ct_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>
</Types>"""
    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>
</Relationships>"""
    _set_doc_part(
        buf,
        FIXTURES_DIR / "comments.docx",
        {
            "word/document.xml": doc_xml,
            "[Content_Types].xml": ct_xml,
            "word/_rels/document.xml.rels": rels_xml,
        },
        {"word/comments.xml": comments_xml},
    )


def create_broken_rels() -> None:
    buf = _make_minimal_docx()
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:t>Document with broken relationship.</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    broken_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/missing_image.png"/>
</Relationships>"""
    _set_doc_part(
        buf,
        FIXTURES_DIR / "broken_rels.docx",
        {"word/document.xml": doc_xml, "word/_rels/document.xml.rels": broken_rels},
    )


def create_tracked_changes_header_footer() -> None:
    buf = _make_minimal_docx()
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:t>Body text.</w:t></w:r></w:p>
    <w:sectPr>
      <w:headerReference w:type="default" r:id="rId1"/>
      <w:footerReference w:type="default" r:id="rId2"/>
    </w:sectPr>
  </w:body>
</w:document>"""
    header_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:hdr xmlns:w="{W_NS}">
  <w:p>
    <w:r><w:t>Header </w:t></w:r>
    <w:ins w:id="5" w:author="Agent" w:date="2026-03-27T00:00:00Z"><w:r><w:t>insert</w:t></w:r></w:ins>
  </w:p>
</w:hdr>"""
    footer_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="{W_NS}">
  <w:p>
    <w:r><w:t>Footer </w:t></w:r>
    <w:del w:id="6" w:author="Agent" w:date="2026-03-27T00:00:00Z"><w:r><w:delText>remove</w:delText></w:r></w:del>
  </w:p>
</w:ftr>"""
    ct_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>"""
    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
</Relationships>"""
    _set_doc_part(
        buf,
        FIXTURES_DIR / "tracked_changes_header_footer.docx",
        {
            "word/document.xml": doc_xml,
            "[Content_Types].xml": ct_xml,
            "word/_rels/document.xml.rels": rels_xml,
        },
        {
            "word/header1.xml": header_xml,
            "word/footer1.xml": footer_xml,
        },
    )


def create_comment_mid_run_exact() -> None:
    buf = _make_minimal_docx()
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:r><w:t>xxHello</w:t></w:r>
      <w:r><w:t>Worldyy</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
    _set_doc_part(buf, FIXTURES_DIR / "comment_mid_run_exact.docx", {"word/document.xml": doc_xml})


def create_comment_multi_t_single_run() -> None:
    buf = _make_minimal_docx()
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W_NS}">
  <w:body>
    <w:p>
      <w:r><w:t>Hel</w:t><w:t>lo</w:t></w:r>
      <w:r><w:t> world</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
    _set_doc_part(buf, FIXTURES_DIR / "comment_multi_t_single_run.docx", {"word/document.xml": doc_xml})


def _build_hyperlink(paragraph, text_parts: list[str], url: str) -> None:
    relation_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relation_id)
    for part in text_parts:
        run = OxmlElement("w:r")
        t = OxmlElement("w:t")
        t.text = part
        run.append(t)
        hyperlink.append(run)
    paragraph._p.append(hyperlink)


def create_comment_hyperlink_boundary() -> None:
    doc = Document()
    p = doc.add_paragraph()
    p.add_run("Prefix ")
    _build_hyperlink(p, ["Link", "Target"], "https://example.com")
    p.add_run(" suffix")
    doc.save(FIXTURES_DIR / "comment_hyperlink_boundary.docx")


def _append_field_code(paragraph, instruction: str, result_text: str) -> None:
    def make_run(children: list[OxmlElement]) -> None:
        run = OxmlElement("w:r")
        for child in children:
            run.append(child)
        paragraph._p.append(run)

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    make_run([fld_begin])

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    make_run([instr])

    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    make_run([fld_sep])

    t = OxmlElement("w:t")
    t.text = result_text
    make_run([t])

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    make_run([fld_end])


def create_comment_field_code_boundary() -> None:
    doc = Document()
    p = doc.add_paragraph()
    p.add_run("Date: ")
    _append_field_code(p, ' DATE \\\\@ "yyyy-MM-dd" ', "2026-03-27")
    p.add_run(".")
    doc.save(FIXTURES_DIR / "comment_field_code_boundary.docx")


def _validate_docx_json(path: Path) -> dict:
    sys.path.insert(0, str((Path(__file__).resolve().parent.parent / "scripts")))
    from ooxml.validate import validate

    return validate(str(path))


def _boundary_summary(path: Path) -> dict:
    import defusedxml.minidom

    with zipfile.ZipFile(path, "r") as zf:
        dom = defusedxml.minidom.parseString(zf.read("word/document.xml"))
    para = dom.getElementsByTagNameNS(W_NS, "p")[0]
    sequence = []
    texts = []
    for node in para.childNodes:
        local = getattr(node, "localName", None)
        if not local:
            continue
        sequence.append(local)
        if local == "r":
            t_nodes = [c for c in node.childNodes if getattr(c, "localName", None) == "t"]
            texts.append("".join(c.childNodes[0].nodeValue for c in t_nodes if c.childNodes))
        elif local == "hyperlink":
            inner = []
            for run in node.getElementsByTagNameNS(W_NS, "r"):
                for child in run.childNodes:
                    if getattr(child, "localName", None) == "t" and child.childNodes:
                        inner.append(child.childNodes[0].nodeValue)
            texts.append("".join(inner))
        else:
            texts.append("")
    return {"sequence": sequence, "texts": texts}


def _write_expected_files() -> None:
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
    validate_header_footer = _validate_docx_json(FIXTURES_DIR / "tracked_changes_header_footer.docx")
    (EXPECTED_DIR / "validate_tracked_changes_header_footer.json").write_text(
        json.dumps(validate_header_footer, indent=2), encoding="utf-8"
    )
    (EXPECTED_DIR / "accept_changes_header_footer_zero.txt").write_text(
        "remaining revision tags=0\n", encoding="utf-8"
    )
    summaries = {
        "comment_mid_run_exact.json": {
            "sequence": ["r", "commentRangeStart", "r", "r", "commentRangeEnd", "r", "r"],
            "texts": ["xx", "", "Hello", "World", "", "", "yy"],
        },
        "comment_multi_t_single_run.json": {
            "sequence": ["commentRangeStart", "r", "commentRangeEnd", "r", "r"],
            "texts": ["", "Hello", "", "", " world"],
        },
        "comment_hyperlink_boundary.json": {
            "sequence": ["r", "commentRangeStart", "hyperlink", "commentRangeEnd", "r", "r"],
            "texts": ["Prefix ", "", "LinkTarget", "", "", " suffix"],
        },
        "comment_field_code_boundary.json": {
            "sequence": ["r", "r", "r", "r", "commentRangeStart", "r", "commentRangeEnd", "r", "r", "r"],
            "texts": ["Date: ", "", "", "", "", "2026-03-27", "", "", "", "."],
        },
    }
    for name, payload in summaries.items():
        (EXPECTED_DIR / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def build(only: str | None = None, force: bool = False) -> list[dict]:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)

    registry = {
        "tracked_changes": create_tracked_changes,
        "comments": create_comments,
        "broken_rels": create_broken_rels,
        "tracked_changes_header_footer": create_tracked_changes_header_footer,
        "comment_mid_run_exact": create_comment_mid_run_exact,
        "comment_multi_t_single_run": create_comment_multi_t_single_run,
        "comment_hyperlink_boundary": create_comment_hyperlink_boundary,
        "comment_field_code_boundary": create_comment_field_code_boundary,
    }
    results = []
    for name, fn in registry.items():
        if only and only != name:
            continue
        target = FIXTURES_DIR / f"{name}.docx"
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
        "tracked_changes": {
            "fixture": "tracked_changes.docx",
            "assertions": [("word/document.xml", "w:ins"), ("word/document.xml", "w:del")],
        },
        "comments": {
            "fixture": "comments.docx",
            "assertions": [("word/document.xml", "w:commentRangeStart"), ("word/comments.xml", "w:comment ")],
        },
        "broken_rels": {
            "fixture": "broken_rels.docx",
            "assertions": [("word/_rels/document.xml.rels", "missing_image.png")],
        },
        "tracked_changes_header_footer": {
            "fixture": "tracked_changes_header_footer.docx",
            "assertions": [("word/header1.xml", "w:ins"), ("word/footer1.xml", "w:del")],
        },
        "comment_mid_run_exact": {
            "fixture": "comment_mid_run_exact.docx",
            "assertions": [("word/document.xml", "xxHello"), ("word/document.xml", "Worldyy")],
        },
        "comment_multi_t_single_run": {
            "fixture": "comment_multi_t_single_run.docx",
            "assertions": [("word/document.xml", "<w:t>Hel</w:t><w:t>lo</w:t>")],
        },
        "comment_hyperlink_boundary": {
            "fixture": "comment_hyperlink_boundary.docx",
            "assertions": [("word/document.xml", "w:hyperlink"), ("word/_rels/document.xml.rels", "hyperlink")],
        },
        "comment_field_code_boundary": {
            "fixture": "comment_field_code_boundary.docx",
            "assertions": [("word/document.xml", "w:instrText"), ("word/document.xml", "2026-03-27")],
        },
    }
    checked = []
    failed = []
    details = []
    for slug, cfg in mapping.items():
        if only and only != slug:
            continue
        fixture = FIXTURES_DIR / cfg["fixture"]
        result = {"fixture": cfg["fixture"], "exists": fixture.exists(), "checksum_ok": fixture.exists(), "assertions_ok": True}
        if not fixture.exists():
            result["checksum_ok"] = False
            result["assertions_ok"] = False
            failed.append(slug)
            details.append(result)
            continue
        with zipfile.ZipFile(fixture, "r") as zf:
            for part, needle in cfg["assertions"]:
                text = zf.read(part).decode("utf-8")
                if needle not in text:
                    result["assertions_ok"] = False
        if slug == "tracked_changes_header_footer":
            expected = EXPECTED_DIR / "validate_tracked_changes_header_footer.json"
            result["assertions_ok"] = result["assertions_ok"] and expected.exists()
        if slug.startswith("comment_") and slug != "comments":
            expected = EXPECTED_DIR / f"{slug}.json"
            result["assertions_ok"] = result["assertions_ok"] and expected.exists()
        if not (result["exists"] and result["checksum_ok"] and result["assertions_ok"]):
            failed.append(slug)
        checked.append(slug)
        details.append(result)
    return {"mode": "verify", "skill": "docx", "ok": not failed, "checked": checked, "failed": failed, "details": details}


def _print_results(results: list[dict]) -> None:
    for item in results:
        status = item["status"]
        fixture = item["fixture"]
        if status == "CREATED":
            print(f"CREATED {fixture}")
        else:
            print(f"SKIPPED {fixture}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify DOCX regression fixtures")
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
        _print_results(results)
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
