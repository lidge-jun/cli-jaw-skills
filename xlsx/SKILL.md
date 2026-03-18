---
name: xlsx
description: "Excel XLSX create, read, edit, analyze. Triggers: Excel, .xlsx, spreadsheet, financial model, data analysis, pivot, chart."
---

# XLSX Skill

Use this skill for any spreadsheet task: create, read, edit, analyze, or format .xlsx/.xlsm/.csv/.tsv files.
Triggers: "Excel", ".xlsx", spreadsheet, financial model, data analysis, pivot, chart.
Also covers: pandas-based data analysis, conditional formatting, data validation, formula workflows, and chart creation.
Do NOT use for: Word documents, HTML reports, standalone Python scripts, database pipelines, or Google Sheets API.

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

### Unified CLI (`xlsx_cli.py`)

All operations are available through a single entrypoint:

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
```

---

## Requirements for All Excel Files

- **Professional Font**: Use a consistent, professional font (e.g., Arial, Times New Roman) for all deliverables unless otherwise instructed
- **Zero Formula Errors**: Every Excel model MUST be delivered with ZERO formula errors (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, `#NAME?`)
- **Preserve Existing Templates**: When modifying files, study and exactly match existing format, style, and conventions. Existing template conventions always override these guidelines.

---

## Creating/Editing: openpyxl

> [openpyxl ReadTheDocs](https://openpyxl.readthedocs.io/en/stable/) — MIT License

```bash
pip install openpyxl
```

### Basic Structure

```python
from openpyxl import Workbook, load_workbook

# New workbook
wb = Workbook()
ws = wb.active
ws.title = "Sales Data"

ws['A1'] = 'Product'
ws['B1'] = 'Revenue'
ws.append(['Widget A', 12500])
ws.append(['Widget B', 8200])

wb.save("output.xlsx")
```

```python
# Read existing
wb = load_workbook('existing.xlsx')
ws = wb.active

for row in ws.iter_rows(min_row=1, max_col=3, values_only=True):
    print(row)
```

> ⚠ Opening with `data_only=True` replaces formulas with values — saving permanently loses formulas

### Styling

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Font
ws['A1'].font = Font(name='Arial', size=14, bold=True, color='FFFFFF')

# Background
ws['A1'].fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')

# Alignment
ws['A1'].alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

# Border
thin_border = Border(
    left=Side(style='thin', color='000000'),
    right=Side(style='thin', color='000000'),
    top=Side(style='thin', color='000000'),
    bottom=Side(style='thin', color='000000')
)
ws['A1'].border = thin_border

# Bold entire header row
for cell in ws[1]:
    cell.font = Font(bold=True)
```

### Tables

```python
from openpyxl.worksheet.table import Table, TableStyleInfo

ws.append(["Fruit", "2023", "2024"])
ws.append(["Apples", 10000, 12000])
ws.append(["Pears", 2000, 3000])

tab = Table(displayName="Table1", ref="A1:C3")
style = TableStyleInfo(
    name="TableStyleMedium9",
    showFirstColumn=False, showLastColumn=False,
    showRowStripes=True, showColumnStripes=True
)
tab.tableStyleInfo = style
ws.add_table(tab)
```

### Formulas

```python
ws['C2'] = '=A2*B2'
ws['D1'] = '=SUM(B2:B10)'
```

> Always use formulas instead of hard-coded values. Values auto-update when data changes.

### CRITICAL: Use Formulas, Not Hardcoded Values

**Always use Excel formulas instead of calculating values in Python and hardcoding them.**

```python
# ❌ WRONG — calculating in Python and hardcoding
total = df['Sales'].sum()
sheet['B10'] = total          # Hardcodes 5000

growth = (df.iloc[-1]['Revenue'] - df.iloc[0]['Revenue']) / df.iloc[0]['Revenue']
sheet['C5'] = growth           # Hardcodes 0.15

avg = sum(values) / len(values)
sheet['D20'] = avg             # Hardcodes 42.5
```

```python
# ✅ CORRECT — let Excel calculate
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to ALL calculations — totals, percentages, ratios, differences. The spreadsheet should recalculate when source data changes.

### Performance Tips for Large Files

```python
# Read-only mode (streaming, low memory)
wb = load_workbook('large.xlsx', read_only=True)
for row in ws.iter_rows(values_only=True):
    process(row)
wb.close()  # Must close read_only workbooks

# Write-only mode (streaming output)
wb = Workbook(write_only=True)
ws = wb.create_sheet()
for data in generate_rows():
    ws.append(data)
wb.save('large_output.xlsx')
```

### Conditional Formatting

```python
from openpyxl.formatting.rule import CellIsRule, FormulaRule, Rule
from openpyxl.styles import PatternFill
from openpyxl.styles.differential import DifferentialStyle

red_fill = PatternFill(start_color='EE1111', end_color='EE1111', fill_type='solid')

# Value comparison
ws.conditional_formatting.add('C2:C10',
    CellIsRule(operator='lessThan', formula=['C$1'], stopIfTrue=True, fill=red_fill))

# Range between
ws.conditional_formatting.add('D2:D10',
    CellIsRule(operator='between', formula=['1','5'], stopIfTrue=True, fill=red_fill))

# Formula-based
ws.conditional_formatting.add('E1:E10',
    FormulaRule(formula=['ISBLANK(E1)'], stopIfTrue=True, fill=red_fill))

# Entire row formatting
dxf = DifferentialStyle(fill=PatternFill(bgColor="FFC7CE"))
r = Rule(type="expression", dxf=dxf, stopIfTrue=True)
r.formula = ['$B2="Microsoft"']
ws.conditional_formatting.add("A1:C10", r)
```

### Data Validation (Dropdowns)

```python
from openpyxl.worksheet.datavalidation import DataValidation

dv = DataValidation(type="list", formula1='"Dog,Cat,Bat"', allow_blank=True)
dv.error = 'Not in list'
dv.errorTitle = 'Invalid'
dv.prompt = 'Select from list'
dv.promptTitle = 'Selection'

ws.add_data_validation(dv)
dv.add(ws["A1"])
dv.add('B1:B1048576')  # entire column
```

### Charts

```python
from openpyxl.chart import BarChart, PieChart, LineChart, Reference

# Bar chart
chart = BarChart()
chart.type = "col"
chart.title = "Quarterly Revenue"
chart.y_axis.title = "Amount ($)"
chart.x_axis.title = "Quarter"

data = Reference(ws, min_col=2, min_row=1, max_col=3, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.style = 10
ws.add_chart(chart, "E1")

# Line chart
line = LineChart()
line.title = "Revenue Trend"
line.style = 13
data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=13)
line.add_data(data, titles_from_data=True)
ws.add_chart(line, "E15")

# Pie chart
pie = PieChart()
pie.title = "Market Share"
data = Reference(ws, min_col=2, min_row=1, max_row=5)
cats = Reference(ws, min_col=1, min_row=2, max_row=5)
pie.add_data(data, titles_from_data=True)
pie.set_categories(cats)
ws.add_chart(pie, "E30")
```

### Chart Style Tips

| Chart Type           | When to Use        | openpyxl style |
| -------------------- | ------------------ | -------------- |
| Column bar (`col`)   | Category comparison| `style=10`     |
| Horizontal bar (`bar`)| Long labels       | `style=11`     |
| Line (`line`)        | Time series trends | `style=13`     |
| Pie                  | Ratios/share       | `style=26`     |
| Area (`area`)        | Cumulative trends  | `style=10`     |

---

## Reading/Analysis: pandas

```python
import pandas as pd

# Read
df = pd.read_excel('file.xlsx')                         # first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None) # all sheets as dict

# Analysis
df.head()
df.info()
df.describe()

# Write
df.to_excel('output.xlsx', index=False)
```

---

## Financial Model Conventions

### Color Coding (Industry Standard)

| Color  | RGB         | Purpose                              |
| ------ | ----------- | ------------------------------------ |
| Blue   | `0,0,255`   | Hard-coded inputs, scenario toggles  |
| Black  | `0,0,0`     | Formulas and calculated results      |
| Green  | `0,128,0`   | Values pulled from other sheets      |
| Red    | `255,0,0`   | External file references             |
| Yellow | `255,255,0` | Key assumptions needing attention    |

### Number Formatting Standards

| Data Type     | Format               | Example                    |
| ------------- | -------------------- | -------------------------- |
| Years         | Text string          | `"2024"` not `2,024`       |
| Currency      | `$#,##0`             | Always specify units in headers: `"Revenue ($mm)"` |
| Zeros         | Show as dash         | `$#,##0;($#,##0);"-"`     |
| Percentages   | `0.0%`               | One decimal default        |
| Multiples     | `0.0x`               | For EV/EBITDA, P/E         |
| Negatives     | Parentheses          | `(123)` not `-123`         |

### Korean Financial Formats

```python
# Korean won (no decimals)
ws['B2'].number_format = '#,##0'
# Auto-convert to 억 (hundred million)
ws['B3'].number_format = '#,##0,,"억"'
# Millions (백만)
ws['B4'].number_format = '#,##0,"백만"'
# Negatives in parentheses
ws['B5'].number_format = '#,##0;(#,##0)'
# VAT (10% fixed)
ws['B6'] = '=ROUND(B2*0.1, 0)'
```

| Data          | Format            | Display         |
| ------------- | ----------------- | --------------- |
| Won           | `#,##0`           | `1,234,567`     |
| Hundred million | `#,##0,,"억"`  | `12억`          |
| Millions      | `#,##0,"백만"`  | `1,235백만`     |
| VAT           | 10% fixed         | `=ROUND(B2*0.1, 0)` |

### 3-Sheet Separation Principle

```
Workbook
├── Inputs        ← Blue text, user-adjustable assumptions
├── Calculations  ← Black text, formulas only (no hard-coding)
└── Outputs       ← Summary dashboard, charts
```

### Document Hard-coded Sources

Always record the source next to input values:
```python
ws['A1'] = 'Revenue Growth Rate'
ws['B1'] = 0.15
ws['C1'] = 'Source: Company 10-K, FY2024, p.45'  # source required
```

### Named Ranges (Formula Readability)

```python
from openpyxl.workbook.defined_name import DefinedName

ref = DefinedName('revenue_growth', attr_text="Inputs!$B$1")
wb.defined_names.add(ref)

# Use in formulas
ws['B2'] = '=revenue_2024 * (1 + revenue_growth)'
# vs unreadable: '=Inputs!$B$5 * (1 + Inputs!$B$1)'
```

---

## Formula Recalculation Workflow

openpyxl does NOT calculate formulas — it stores them as strings only.

### Method 1: recalc script

```bash
python scripts/recalc.py output.xlsx
# Returns JSON with error details
```

### Method 2: LibreOffice headless

```bash
soffice --headless --calc --convert-to xlsx output.xlsx
```

### Method 3: Open in Excel

Excel auto-recalculates on open. Most reliable but not automatable.

> **Always include a recalculation step when using formulas.** The xlsx saved by openpyxl has empty or stale formula results.

### Common Workflow

1. **Choose tool**: pandas for data analysis, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas** (MANDATORY IF USING FORMULAS): `python scripts/recalc.py output.xlsx`
6. **Verify and fix errors**: If `status` is `errors_found`, check `error_summary` for error types/locations, fix, and recalculate again

### Interpreting recalc.py Output

The script returns JSON with error details:
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

Common errors:
- `#REF!`: Invalid cell references
- `#DIV/0!`: Division by zero — add `=IF(B2=0, 0, A2/B2)` guards
- `#VALUE!`: Wrong data type in formula
- `#NAME?`: Unrecognized formula name

### Formula Verification Checklist

**Essential Verification:**
- [ ] Test 2-3 sample references: verify they pull correct values before building full model
- [ ] Column mapping: confirm Excel columns match (e.g., column 64 = BL, not BK)
- [ ] Row offset: remember Excel rows are 1-indexed (DataFrame row 5 = Excel row 6)

**Common Pitfalls:**
- [ ] NaN handling: check for null values with `pd.notna()`
- [ ] Far-right columns: FY data often in columns 50+
- [ ] Multiple matches: search all occurrences, not just first
- [ ] Division by zero: check denominators before using `/` in formulas
- [ ] Cross-sheet references: use correct format (`Sheet1!A1`)

**Formula Testing Strategy:**
- [ ] Start small: test formulas on 2-3 cells before applying broadly
- [ ] Verify dependencies: check all cells referenced in formulas exist
- [ ] Test edge cases: include zero, negative, and very large values

---

## OOXML Direct Editing

For modifying xlsx structure at the XML level.

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

```bash
python scripts/ooxml/unpack.py workbook.xlsx unpacked/
# Edit XML
python scripts/ooxml/pack.py unpacked/ output.xlsx --original workbook.xlsx

# Validate structure
python scripts/ooxml/validate.py output.xlsx --json
# Returns: {"passed": bool, "errors": [...], "warnings": [...], "stats": {...}}

# Auto-repair (if validation fails)
python scripts/ooxml/repair.py output.xlsx
# Returns: {"repaired": int, "details": [...]}
```

---

## Anti-Patterns

| ❌ Don't                          | ✅ Do Instead                        | Why                              |
| --------------------------------- | ----------------------------------- | -------------------------------- |
| Hard-code values instead of formulas | Use `=SUM(B2:B10)` etc.         | Auto-update when data changes    |
| Open with `data_only=True` & save | Keep `data_only=False` (default)    | Permanently loses formulas       |
| Off-by-one range                  | Double-check `min_row`, `max_row`   | Leading cause of missing data    |
| Use only first search result      | Scan full column/row                | FY data could be in 50+ columns  |
| Divide without denominator check  | `=IF(B2=0, 0, A2/B2)`              | Prevents `#DIV/0!`              |
| Ignore circular references        | Verify formula chains               | Infinite loop = file corruption  |
| Skip formula recalculation        | Run soffice or recalc.py            | Formula results will be missing  |
| CJK columns with default width    | Use `auto_fit_columns()` from cjk_utils | Korean `###` truncation          |

---

## QA Verification

```bash
# Check results in Python
python -c "
from openpyxl import load_workbook
wb = load_workbook('output.xlsx', data_only=True)
ws = wb.active
for row in ws.iter_rows(max_row=5, values_only=True):
    print(row)
"

# Visual check via LibreOffice
soffice --headless --convert-to pdf output.xlsx
```

Checklist:
- [ ] Formulas reference correct cell ranges
- [ ] Formula recalculation completed (`recalc.py` or soffice)
- [ ] Color coding followed (blue=input, black=formula)
- [ ] No off-by-one data range errors
- [ ] No `#DIV/0!`, `#REF!`, `#N/A` errors
- [ ] Conditional formatting applied as intended
- [ ] Data validation dropdowns working
- [ ] Named ranges mapped correctly
- [ ] No circular references
- [ ] Korean text visible in full (no `###` truncation)
- [ ] Color contrast >= 4.5:1
- [ ] Korean font (Noto Sans KR / Malgun Gothic) renders correctly
- [ ] Column widths accommodate full-width Korean characters
- [ ] recalc.py returns `status: success` with 0 errors

---

## CJK / Korean Text Handling

### Column Width for CJK

CJK characters are full-width (~2× Latin width). openpyxl's auto-sizing does not account for this. Use the CJK-aware auto-fit utility:

```python
from scripts.ooxml.cjk_utils import auto_fit_columns

# After populating worksheet data
auto_fit_columns(ws, padding=3, max_width=50)
wb.save('output.xlsx')
```

Or calculate widths manually:

```python
from scripts.ooxml.cjk_utils import get_display_width

get_display_width("Revenue")      # 7
get_display_width("매출액")        # 6  (3 Korean chars × 2)
get_display_width("Revenue 매출")  # 12 (7 Latin + 1 space + 4 Korean)
```

### Korean Fonts

```python
from openpyxl.styles import Font

# Cross-platform safe
ko_font = Font(name="Noto Sans KR", size=11)

# Windows-only environments
ko_font = Font(name="Malgun Gothic", size=11)

# Header
ko_header = Font(name="Noto Sans KR", size=12, bold=True)
```

> `charset=134` is NOT needed. Modern xlsx uses UTF-8 internally. Setting charset can cause encoding confusion in some viewers.

Recommended fonts:

| Font               | License   | Cross-platform | Best for           |
| ------------------ | --------- | -------------- | ------------------ |
| Noto Sans KR       | OFL       | Win/Mac/Linux  | Safest choice      |
| Pretendard         | OFL       | Win/Mac/Linux  | Modern UI          |
| Malgun Gothic      | MS bundle | Windows only   | Windows-only files |
| NanumGothic        | OFL       | Win/Mac/Linux  | General Korean     |

### PivotTable Alternative

openpyxl cannot create PivotTables (read/preserve only). Workarounds:

```python
# Method 1: pandas pivot → new sheet
import pandas as pd
df = pd.read_excel('data.xlsx')
pivot = pd.pivot_table(df, values='Revenue', index='Product', columns='Quarter', aggfunc='sum')
pivot.to_excel('pivot_output.xlsx', sheet_name='PivotResult')

# Method 2: template with existing PivotTable — update data sheet only
wb = load_workbook('pivot_template.xlsx')
ws = wb['RawData']
# Replace data rows...
wb.save('updated_pivot.xlsx')
# Open in Excel → Refresh All to update PivotTable
```

---

## Template Preservation

When modifying existing files, **never alter styles, formatting, or structure beyond what was requested.**

```python
# Load without data_only — preserves formulas
wb = load_workbook('template.xlsx')  # data_only=False (default)
ws = wb.active

# Replace placeholders only — preserve cell styles
for row in ws.iter_rows():
    for cell in row:
        if cell.value and isinstance(cell.value, str):
            if '{{COMPANY}}' in cell.value:
                cell.value = cell.value.replace('{{COMPANY}}', 'ABC Corp')
        # Do NOT touch cell.font, cell.fill, cell.border — preserves styling

wb.save('filled_template.xlsx')
```

Rules:
- Never delete existing `ConditionalFormatting`
- Never delete existing `DataValidation`
- Never overwrite cell styles (`font`, `fill`, `border`) unless requested
- Never remove `DefinedName` (named ranges)
- When extending data ranges, verify existing chart references first

---

## Accessibility (WCAG 2.1 AA)

| Requirement        | Standard          | Implementation                          |
| ------------------ | ----------------- | --------------------------------------- |
| Color contrast     | >= 4.5:1          | Use `cjk_utils.check_contrast()` to verify |
| Sheet tab names    | Descriptive       | `ws.title = "Sales Data"` not `"Sheet1"` |
| Table headers      | Marked as header  | `tab.headerRowCount = 1`                |
| Chart titles       | Always present    | Acts as alt text for charts             |
| Minimum font size  | >= 10pt           | No captions below 10pt                  |

```python
from scripts.ooxml.cjk_utils import check_contrast

# Verify text/background contrast
ratio = check_contrast("FFFFFF", "4472C4")
assert ratio >= 4.5, f"Contrast insufficient: {ratio:.1f}:1 (need >= 4.5:1)"

# Descriptive sheet names
ws.title = "Revenue Summary"  # ✅
# ws.title = "Sheet1"         # ❌

# Table header for screen readers
tab = Table(displayName="SalesData", ref="A1:D10")
tab.headerRowCount = 1

# Chart title (serves as alt text)
chart.title = "Quarterly Revenue Comparison 2024-2025"
```

---

## Code Style Guidelines

**Python code for Excel operations:**
- Write minimal, concise code without unnecessary comments
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

**For Excel files:**
- Add cell comments for complex formulas or important assumptions
- Document data sources for hardcoded values

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
