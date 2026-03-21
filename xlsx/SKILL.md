---
name: xlsx
description: "Excel XLSX create, read, edit, analyze. Triggers: Excel, .xlsx, spreadsheet, financial model, data analysis, pivot, chart."
---

# XLSX Skill

Handle spreadsheet tasks: create, read, edit, analyze, or format .xlsx/.xlsm/.csv/.tsv files.
Also covers: pandas-based analysis, conditional formatting, data validation, formula workflows, and chart creation.

---

## Quick Reference

| Task         | Tool                                             |
| ------------ | ------------------------------------------------ |
| **Create**   | `openpyxl` (Python) — Excel 2010+ xlsx/xlsm      |
| **Read**     | `pandas` or `openpyxl`                           |
| **Analyze**  | `pandas`                                         |
| **Edit XML** | Unpack → XML Edit → Pack (OOXML workflow)         |
| **Recalc**   | `scripts/recalc.py` or soffice headless           |
| **Review**   | soffice → PDF → visual inspection                |
| **Search**   | `xlsx_cli.py search input.xlsx "pattern" [--json]` |

### Unified CLI (`xlsx_cli.py`)

```bash
# Unpack / Pack
python scripts/xlsx_cli.py open input.xlsx work/
python scripts/xlsx_cli.py save work/ output.xlsx

# Validation & Repair
python scripts/xlsx_cli.py validate input.xlsx --json
python scripts/xlsx_cli.py repair input.xlsx              # dry-run (default)
python scripts/xlsx_cli.py repair input.xlsx --apply       # actually fix

# Recalculation
python scripts/xlsx_cli.py recalc input.xlsx output.xlsx
python scripts/xlsx_cli.py recalc input.xlsx output.xlsx --check-errors

# Exploration
python scripts/xlsx_cli.py text input.xlsx
python scripts/xlsx_cli.py sheet-overview input.xlsx --json
python scripts/xlsx_cli.py formula-audit input.xlsx --json

# Search
python scripts/xlsx_cli.py search input.xlsx "pattern" --json
python scripts/xlsx_cli.py search input.xlsx "pattern" --sheet "Sheet1"
```

---

## Core Rules

1. **Use Excel formulas, not hardcoded values** — spreadsheets should recalculate when source data changes
2. **Zero formula errors** — deliver with no `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?` errors
3. **Recalculate after saving** — openpyxl stores formulas as strings only; run `recalc.py` or soffice
4. **Preserve existing templates** — when modifying files, match existing format, style, and conventions exactly
5. **Use professional fonts** — Arial, Times New Roman, or Noto Sans KR for Korean content
6. **Use `auto_fit_columns()` for CJK** — Korean characters are full-width; default sizing causes `###` truncation

---

## Creating/Editing: openpyxl

See `references/openpyxl_guide.md` for complete examples (styling, tables, conditional formatting, data validation, charts, named ranges, performance tips).

### Essential Patterns

```python
from openpyxl import Workbook, load_workbook

wb = Workbook()
ws = wb.active
ws.title = "Sales Data"
ws.append(['Product', 'Revenue'])
ws.append(['Widget A', 12500])
wb.save("output.xlsx")
```

> Opening with `data_only=True` replaces formulas with cached values — saving permanently loses formulas.

### Use Formulas, Not Hardcoded Values

```python
# ❌ Calculating in Python and hardcoding
total = df['Sales'].sum()
sheet['B10'] = total

# ✅ Let Excel calculate
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to all calculations — totals, percentages, ratios, differences.

---

## Reading/Analysis: pandas

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                          # first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # all sheets as dict
df.to_excel('output.xlsx', index=False)
```

---

## Formula Recalculation

openpyxl does not calculate formulas — it stores them as strings only. Recalculate after every save.

### Methods

| Method | Command | Notes |
|--------|---------|-------|
| recalc script | `python scripts/recalc.py output.xlsx` | Returns JSON with error details |
| LibreOffice | `soffice --headless --calc --convert-to xlsx output.xlsx` | Reliable |
| Open in Excel | Manual open | Auto-recalculates; not automatable |

### Workflow

1. Create/modify workbook with openpyxl
2. Save to file
3. Recalculate: `python scripts/recalc.py output.xlsx`
4. Check output — if `status: errors_found`, fix errors and recalculate again

### Interpreting recalc.py Output

```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {"count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"]}
  }
}
```

Common errors:
- `#REF!` — invalid cell references
- `#DIV/0!` — guard with `=IF(B2=0, 0, A2/B2)`
- `#VALUE!` — wrong data type in formula
- `#NAME?` — unrecognized formula name

### Formula Verification Checklist

- [ ] Test 2-3 sample references before building full model
- [ ] Column mapping: confirm Excel columns match (column 64 = BL, not BK)
- [ ] Row offset: Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)
- [ ] NaN handling: check for null values with `pd.notna()`
- [ ] Division by zero: check denominators before `/` in formulas
- [ ] Cross-sheet references: use correct format (`Sheet1!A1`)

---

## Financial Model Conventions

See `references/financial_conventions.md` for complete color coding, number formatting, Korean formats, 3-sheet separation, and source documentation standards.

Key principles:
- **Blue** text = inputs, **Black** = formulas, **Green** = cross-sheet refs
- Separate into Inputs / Calculations / Outputs sheets
- Document data sources next to hardcoded values
- Korean won format: `#,##0` | 억 unit: `#,##0,,"억"`

---

## OOXML Direct Editing

For modifying xlsx structure at the XML level:

```bash
python scripts/ooxml/unpack.py workbook.xlsx unpacked/
# Edit XML files
python scripts/ooxml/pack.py unpacked/ output.xlsx --original workbook.xlsx

# Validate structure
python scripts/ooxml/validate.py output.xlsx --json

# Auto-repair (if validation fails)
python scripts/ooxml/repair.py output.xlsx
```

### File Structure

```
unpacked/
├── [Content_Types].xml
├── xl/
│   ├── workbook.xml       ← Sheet list
│   ├── sharedStrings.xml  ← Shared string table
│   ├── styles.xml         ← Style definitions
│   ├── worksheets/
│   │   ├── sheet1.xml     ← Individual sheet data
│   │   └── _rels/
│   ├── charts/            ← Chart definitions
│   └── media/             ← Images
└── docProps/
```

---

## Template Preservation

When modifying existing files, only change what was requested:

```python
wb = load_workbook('template.xlsx')  # data_only=False (default) preserves formulas
ws = wb.active

for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str):
            if '{{COMPANY}}' in cell.value:
                cell.value = cell.value.replace('{{COMPANY}}', 'ABC Corp')
        # Preserve cell.font, cell.fill, cell.border untouched

wb.save('filled_template.xlsx')
```

Rules:
- Preserve existing `ConditionalFormatting`, `DataValidation`, `DefinedName` (named ranges)
- Preserve cell styles (`font`, `fill`, `border`) unless changes were requested
- When extending data ranges, verify existing chart references first

---

## CJK / Korean Text

Use `auto_fit_columns()` for CJK content — openpyxl's auto-sizing mishandles full-width characters:

```python
from scripts.ooxml.cjk_utils import auto_fit_columns
auto_fit_columns(ws, padding=3, max_width=50)
```

Preferred font: `Noto Sans KR` (cross-platform, OFL license).

See `references/cjk_handling.md` for Korean fonts, PivotTable alternatives, and accessibility (WCAG 2.1 AA).

---

## Anti-Patterns

| Avoid | Use Instead | Why |
| ----- | ----------- | --- |
| Hardcode calculated values | `=SUM(B2:B10)` etc. | Auto-update when data changes |
| `data_only=True` + save | `data_only=False` (default) | Permanently loses formulas |
| Off-by-one ranges | Double-check `min_row`, `max_row` | Leading cause of missing data |
| Only first search result | Scan full column/row | FY data could be in 50+ columns |
| Divide without check | `=IF(B2=0, 0, A2/B2)` | Prevents `#DIV/0!` |
| Skip recalculation | Run soffice or recalc.py | Formula results will be missing |
| Default width for CJK | `auto_fit_columns()` | Korean `###` truncation |

---

## QA Checklist

```bash
# Spot-check in Python
python -c "
from openpyxl import load_workbook
wb = load_workbook('output.xlsx', data_only=True)
ws = wb.active
for row in ws.iter_rows(max_row=5, values_only=True):
    print(row)
"

# Visual check via PDF
soffice --headless --convert-to pdf output.xlsx
```

- [ ] Formulas reference correct cell ranges
- [ ] `recalc.py` returns `status: success` with 0 errors
- [ ] Color coding followed (blue=input, black=formula)
- [ ] No `#DIV/0!`, `#REF!`, `#N/A` errors
- [ ] Conditional formatting and data validation working
- [ ] Korean text visible in full (no `###` truncation)
- [ ] Color contrast >= 4.5:1

---

## Dependencies

```bash
pip install openpyxl           # Excel read/write
pip install pandas             # Data analysis
pip install xlsxwriter         # Advanced charts (alternative)
pip install defusedxml          # Safe XML parsing (validate.py, repair.py)
# LibreOffice (soffice)        # Formula recalculation, PDF conversion
# scripts/ooxml/cjk_utils.py  # Korean: width calc, lang injection, contrast check
```
