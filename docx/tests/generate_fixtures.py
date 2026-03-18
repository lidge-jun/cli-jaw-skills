#!/usr/bin/env python3
"""Generate DOCX test fixture files.

Creates minimal DOCX files for regression testing:
    fixtures/tracked_changes.docx  — Document with tracked insertions/deletions
    fixtures/comments.docx         — Document with comment annotations
    fixtures/broken_rels.docx      — Document with orphan relationship entry
"""

from __future__ import annotations

import io
import shutil
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _make_minimal_docx() -> io.BytesIO:
    """Create a minimal valid DOCX in memory."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # [Content_Types].xml
        zf.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")

        # _rels/.rels
        zf.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")

        # word/document.xml (minimal)
        W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        zf.writestr("word/document.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}">
  <w:body>
    <w:p><w:r><w:t>Minimal document.</w:t></w:r></w:p>
  </w:body>
</w:document>""")

        # word/_rels/document.xml.rels (empty)
        zf.writestr("word/_rels/document.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>""")

    buf.seek(0)
    return buf


def create_tracked_changes():
    """DOCX with tracked insertions and deletions."""
    buf = _make_minimal_docx()
    # Rebuild with tracked changes in document.xml
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p>
      <w:r><w:t>Normal paragraph text.</w:t></w:r>
    </w:p>
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

    out = FIXTURES_DIR / "tracked_changes.docx"
    with zipfile.ZipFile(buf, "r") as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            if item == "word/document.xml":
                dst.writestr(item, doc_xml)
            else:
                dst.writestr(item, src.read(item))
    print(f"  Created: {out.name}")


def create_comments():
    """DOCX with comment annotations."""
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}" xmlns:r="{R}">
  <w:body>
    <w:p>
      <w:r><w:t>Introduction paragraph.</w:t></w:r>
    </w:p>
    <w:p>
      <w:commentRangeStart w:id="0"/>
      <w:r><w:t>This text has a comment attached.</w:t></w:r>
      <w:commentRangeEnd w:id="0"/>
      <w:r>
        <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
        <w:commentReference w:id="0"/>
      </w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Final paragraph without comments.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""

    comments_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="{W}">
  <w:comment w:id="0" w:author="Reviewer" w:date="2026-02-01T09:00:00Z">
    <w:p>
      <w:r><w:t>Please review this section.</w:t></w:r>
    </w:p>
  </w:comment>
</w:comments>"""

    out = FIXTURES_DIR / "comments.docx"
    buf = _make_minimal_docx()
    with zipfile.ZipFile(buf, "r") as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            if item == "word/document.xml":
                dst.writestr(item, doc_xml)
            elif item == "[Content_Types].xml":
                ct = src.read(item).decode("utf-8")
                ct = ct.replace("</Types>",
                    '  <Override PartName="/word/comments.xml" '
                    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>\n'
                    '</Types>')
                dst.writestr(item, ct)
            elif item == "word/_rels/document.xml.rels":
                rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>
</Relationships>"""
                dst.writestr(item, rels)
            else:
                dst.writestr(item, src.read(item))
        dst.writestr("word/comments.xml", comments_xml)
    print(f"  Created: {out.name}")


def create_broken_rels():
    """DOCX with orphan relationship pointing to missing file."""
    buf = _make_minimal_docx()
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{W}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p><w:r><w:t>Document with broken relationship.</w:t></w:r></w:p>
  </w:body>
</w:document>"""

    broken_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/missing_image.png"/>
</Relationships>"""

    out = FIXTURES_DIR / "broken_rels.docx"
    with zipfile.ZipFile(buf, "r") as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            if item == "word/document.xml":
                dst.writestr(item, doc_xml)
            elif item == "word/_rels/document.xml.rels":
                dst.writestr(item, broken_rels)
            else:
                dst.writestr(item, src.read(item))
    print(f"  Created: {out.name}")


def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating DOCX fixtures...")
    create_tracked_changes()
    create_comments()
    create_broken_rels()
    print("Done.")


if __name__ == "__main__":
    main()
