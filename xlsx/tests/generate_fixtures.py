#!/usr/bin/env python3
"""Generate XLSX test fixture files.

Creates minimal XLSX files for regression testing:
    fixtures/formula_errors.xlsx  — XLSX with #REF!, #DIV/0! formula errors
    fixtures/multi_sheet.xlsx     — XLSX with 3 sheets for overview test
    fixtures/broken_refs.xlsx     — XLSX with broken sharedStrings reference
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import openpyxl

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# OOXML namespaces
PKG_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
SS_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def create_formula_errors():
    """XLSX with formula error values."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Errors"

    # Normal cells
    ws["A1"] = "Label"
    ws["B1"] = "Value"
    ws["A2"] = "Valid"
    ws["B2"] = 42

    # Formula that works
    ws["A3"] = "Sum"
    ws["B3"] = "=B2+10"

    # Division by zero
    ws["A4"] = "DivZero"
    ws["B4"] = "=B2/0"

    # We'll inject error values directly after saving
    out = FIXTURES_DIR / "formula_errors.xlsx"
    wb.save(out)

    # Now inject actual error cached values into the XML
    buf = io.BytesIO()
    with zipfile.ZipFile(out, "r") as src, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            data = src.read(item)
            if item.endswith("sheet1.xml"):
                text = data.decode("utf-8")
                # Add a cell with #REF! error value
                # Find </sheetData> and insert error row before it
                error_row = (
                    '<row r="5"><c r="A5" t="str"><v>RefErr</v></c>'
                    '<c r="B5" t="e"><v>#REF!</v></c></row>'
                    '<row r="6"><c r="A6" t="str"><v>NameErr</v></c>'
                    '<c r="B6" t="e"><v>#NAME?</v></c></row>'
                )
                text = text.replace("</sheetData>", error_row + "</sheetData>")
                dst.writestr(item, text)
            else:
                dst.writestr(item, data)

    buf.seek(0)
    out.write_bytes(buf.read())
    print(f"  Created: {out.name}")


def create_multi_sheet():
    """XLSX with 3 sheets for overview testing."""
    wb = openpyxl.Workbook()

    # Sheet 1: Sales
    ws1 = wb.active
    ws1.title = "Sales"
    ws1["A1"] = "Product"
    ws1["B1"] = "Revenue"
    ws1["A2"] = "Widget A"
    ws1["B2"] = 1500
    ws1["A3"] = "Widget B"
    ws1["B3"] = 2300
    ws1["A4"] = "Total"
    ws1["B4"] = "=SUM(B2:B3)"

    # Sheet 2: Inventory
    ws2 = wb.create_sheet("Inventory")
    ws2["A1"] = "Item"
    ws2["B1"] = "Quantity"
    ws2["C1"] = "Location"
    ws2["A2"] = "Widget A"
    ws2["B2"] = 100
    ws2["C2"] = "Warehouse 1"
    ws2["A3"] = "Widget B"
    ws2["B3"] = 50
    ws2["C3"] = "Warehouse 2"

    # Sheet 3: Summary
    ws3 = wb.create_sheet("Summary")
    ws3["A1"] = "Report Date"
    ws3["B1"] = "2026-03-18"
    ws3["A2"] = "Total Revenue"
    ws3["B2"] = "=Sales!B4"

    out = FIXTURES_DIR / "multi_sheet.xlsx"
    wb.save(out)
    print(f"  Created: {out.name}")


def create_broken_refs():
    """XLSX with broken sharedStrings — Content_Types references missing part."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data"
    ws["A1"] = "Hello"
    ws["A2"] = "World"

    out = FIXTURES_DIR / "broken_refs.xlsx"
    wb.save(out)

    # Inject a broken Override in Content_Types pointing to missing file
    buf = io.BytesIO()
    with zipfile.ZipFile(out, "r") as src, zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.namelist():
            data = src.read(item)
            if item == "[Content_Types].xml":
                text = data.decode("utf-8")
                text = text.replace("</Types>",
                    '  <Override PartName="/xl/charts/chart1.xml" '
                    'ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>\n'
                    '</Types>')
                dst.writestr(item, text)
            elif item.endswith(".rels") and "xl/_rels" in item:
                # Add a broken relationship
                text = data.decode("utf-8")
                text = text.replace("</Relationships>",
                    '  <Relationship Id="rId99" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart" '
                    'Target="charts/chart1.xml"/>\n'
                    '</Relationships>')
                dst.writestr(item, text)
            else:
                dst.writestr(item, data)

    buf.seek(0)
    out.write_bytes(buf.read())
    print(f"  Created: {out.name}")


def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating XLSX fixtures...")
    create_formula_errors()
    create_multi_sheet()
    create_broken_refs()
    print("Done.")


if __name__ == "__main__":
    main()
