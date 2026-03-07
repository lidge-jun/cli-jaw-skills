"""Accept all tracked changes in a DOCX file via LibreOffice macro.

Runs LibreOffice in headless mode with a Basic macro that accepts
all insertions, deletions, and format changes, then saves the result.

Usage:
    python accept_changes.py <input.docx> <output.docx>
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from ooxml.soffice import run_soffice

MACRO_SCRIPT = """\
Sub AcceptAllChanges(url As String, outUrl As String)
    Dim oDoc As Object
    Dim oChanges As Object

    oDoc = StarDesktop.loadComponentFromURL( _
        ConvertToURL(url), "_blank", 0, _
        Array(MakePropertyValue("Hidden", True)))

    If IsNull(oDoc) Or IsEmpty(oDoc) Then
        MsgBox "Failed to open document"
        Exit Sub
    End If

    oChanges = oDoc.getRedlines()
    If Not IsNull(oChanges) Then
        oDoc.setPropertyValue("RedlineProtectionKey", Array())
        oDoc.setPropertyValue("RecordChanges", False)
        oDoc.getRedlines().acceptAllChanges()
    End If

    oDoc.store()
    oDoc.close(True)
End Sub

Function MakePropertyValue(sName As String, vValue) As com.sun.star.beans.PropertyValue
    Dim oPropertyValue As New com.sun.star.beans.PropertyValue
    oPropertyValue.Name = sName
    oPropertyValue.Value = vValue
    MakePropertyValue = oPropertyValue
End Function
"""


def accept_changes(input_path: str, output_path: str) -> str:
    """Accept all tracked changes in a DOCX file."""
    src = Path(input_path).resolve()
    dst = Path(output_path).resolve()

    if not src.exists():
        return f"Error: {input_path} does not exist"

    if not src.suffix.lower() == ".docx":
        return f"Error: {input_path} must be a .docx file"

    try:
        # Copy to output first (soffice will modify in place)
        shutil.copy2(src, dst)

        # Run macro via headless soffice
        result = run_soffice(
            [
                "--headless",
                "--invisible",
                f"macro:///Standard.Module1.AcceptAllChanges({dst})",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            # Fallback: try python-docx approach (import change acceptance)
            return _fallback_accept(src, dst)

        return f"Accepted all tracked changes: {input_path} → {output_path}"

    except Exception as e:
        return f"Error: {e}"


def _fallback_accept(src: Path, dst: Path) -> str:
    """Fallback: use OOXML manipulation to accept tracked changes.

    This removes revision markup elements (w:ins, w:del, w:rPrChange, etc.)
    and keeps/removes their content appropriately.
    """
    import zipfile

    import defusedxml.minidom

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        with zipfile.ZipFile(src, "r") as zf:
            zf.extractall(tmp_path)

        doc_xml = tmp_path / "word" / "document.xml"
        if not doc_xml.exists():
            return "Error: not a valid DOCX (missing word/document.xml)"

        dom = defusedxml.minidom.parseString(doc_xml.read_bytes())

        # Accept insertions: unwrap w:ins (keep children)
        for ins in list(dom.getElementsByTagNameNS("*", "ins")):
            parent = ins.parentNode
            for child in list(ins.childNodes):
                parent.insertBefore(child, ins)
            parent.removeChild(ins)

        # Accept deletions: remove w:del entirely
        for del_elem in list(dom.getElementsByTagNameNS("*", "del")):
            del_elem.parentNode.removeChild(del_elem)

        # Remove format change markers
        for tag in ("rPrChange", "pPrChange", "tblPrChange", "trPrChange", "tcPrChange", "sectPrChange"):
            for elem in list(dom.getElementsByTagNameNS("*", tag)):
                elem.parentNode.removeChild(elem)

        doc_xml.write_bytes(dom.toxml(encoding="UTF-8"))

        # Repack
        with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in tmp_path.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(tmp_path))

    return f"Accepted all tracked changes (fallback): {src} → {dst}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Accept all tracked changes in a DOCX file"
    )
    parser.add_argument("input_file", help="Input DOCX with tracked changes")
    parser.add_argument("output_file", help="Output DOCX with changes accepted")
    args = parser.parse_args()

    msg = accept_changes(args.input_file, args.output_file)
    print(msg)
    sys.exit(1 if msg.startswith("Error") else 0)
