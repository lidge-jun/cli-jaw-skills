---
name: xlsx
description: "Use this skill any time a spreadsheet file is the primary input or output (.xlsx, .xlsm, .csv, .tsv). This includes: creating, reading, editing, analyzing, or formatting spreadsheets; cleaning messy tabular data; converting between formats; and data visualization with charts. Also use for pandas-based data analysis when the deliverable is a spreadsheet. Do NOT trigger when the primary deliverable is a Word document, HTML report, standalone Python script, database pipeline, or Google Sheets API integration."
license: Proprietary. LICENSE.txt has complete terms
---

# Requirements for Outputs

## All Excel files

### Professional Font
- Use a consistent, professional font (e.g., Arial, Times New Roman) unless otherwise instructed

### Zero Formula Errors
- Deliver with zero formula errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?)

### Preserve Existing Templates
- Study and match existing format, style, and conventions when modifying files
- Existing template conventions override these guidelines

## Financial models

### Color Coding Standards
Unless otherwise stated by the user or existing template:

- **Blue text (0,0,255)**: Hardcoded inputs and scenario-adjustable numbers
- **Black text (0,0,0)**: Formulas and calculations
- **Green text (0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (255,0,0)**: External links to other files
- **Yellow background (255,255,0)**: Key assumptions needing attention

### Number Formatting Standards

- **Years**: Format as text strings ("2024" not "2,024")
- **Currency**: Use $#,##0 format; specify units in headers ("Revenue ($mm)")
- **Zeros**: Display as "-" including percentages (e.g., "$#,##0;($#,##0);-")
- **Percentages**: Default to 0.0% format (one decimal)
- **Multiples**: Format as 0.0x for valuation multiples (EV/EBITDA, P/E)
- **Negative numbers**: Use parentheses (123) not minus -123

### Formula Construction Rules

- Place all assumptions (growth rates, margins, multiples) in separate cells; use cell references instead of hardcoded values in formulas
  - Example: Use `=B5*(1+$B$6)` instead of `=B5*1.05`
- Verify all cell references, check for off-by-one errors in ranges
- Ensure consistent formulas across all projection periods
- Test with edge cases (zero values, negative numbers)
- Comment hardcoded values with source: "Source: [System], [Date], [Reference], [URL if applicable]"

# XLSX creation, editing, and analysis

## Use Formulas, Not Hardcoded Values

Use Excel formulas instead of calculating values in Python and hardcoding them — this keeps the spreadsheet dynamic and updateable.

### ❌ Wrong — hardcoded
```python
total = df['Sales'].sum()
sheet['B10'] = total  # Hardcodes 5000
```

### ✅ Correct — formula
```python
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5'] = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

This applies to all calculations — totals, percentages, ratios, differences.

## Common Workflow

1. **Choose tool**: pandas for data analysis, openpyxl for formulas/formatting
2. **Create/Load**: Create new workbook or load existing file
3. **Modify**: Add/edit data, formulas, and formatting
4. **Save**: Write to file
5. **Recalculate formulas** (when using formulas): `python scripts/recalc.py output.xlsx`
6. **Verify and fix errors**:
   - The script returns JSON with error details
   - If `status` is `errors_found`, check `error_summary` for specific error types and locations
   - Fix identified errors and recalculate again

**LibreOffice** is available for recalculation via `scripts/recalc.py`. The script auto-configures LibreOffice on first run.

### Creating new Excel files

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet.append(['Row', 'of', 'data'])
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

### Editing existing Excel files

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName']
sheet['A1'] = 'New Value'
sheet.insert_rows(2)
new_sheet = wb.create_sheet('NewSheet')
wb.save('modified.xlsx')
```

## Recalculating formulas

```bash
python scripts/recalc.py <excel_file> [timeout_seconds]
```

The script:
- Recalculates all formulas in all sheets
- Scans all cells for Excel errors (#REF!, #DIV/0!, etc.)
- Returns JSON with detailed error locations and counts

## Formula Verification Checklist

- [ ] Test 2-3 sample references before building full model
- [ ] Confirm column mapping (e.g., column 64 = BL, not BK)
- [ ] Account for row offset (DataFrame row 5 = Excel row 6)
- [ ] Handle NaN with `pd.notna()`
- [ ] Check denominators before `/` in formulas
- [ ] Verify cross-sheet references use correct format (Sheet1!A1)
- [ ] Start small: test formulas on 2-3 cells before applying broadly

### Interpreting recalc.py Output
```json
{
  "status": "success",
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {}
}
```

## Library Selection

- **pandas**: Data analysis, bulk operations, simple data export
- **openpyxl**: Complex formatting, formulas, Excel-specific features

### openpyxl tips
- Cell indices are 1-based (row=1, column=1 = A1)
- Use `data_only=True` to read calculated values — but saving afterward replaces formulas with values permanently
- For large files: use `read_only=True` or `write_only=True`

### pandas tips
- Specify data types to avoid inference issues: `pd.read_excel('file.xlsx', dtype={'id': str})`
- For large files: `pd.read_excel('file.xlsx', usecols=['A', 'C', 'E'])`
- Handle dates: `pd.read_excel('file.xlsx', parse_dates=['date_column'])`
