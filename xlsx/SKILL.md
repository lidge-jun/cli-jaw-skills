---
name: xlsx
description: "Excel XLSX create, read, edit, analyze. Triggers: Excel, .xlsx, spreadsheet, financial model, data analysis, pivot, chart."
---

# XLSX Skill

Use this skill for `.xlsx`, `.xlsm`, `.csv`, and `.tsv` work that ends in an Excel workbook.
Primary tool: **officecli** for workbook mutation and inspection.
Primary data pipeline: **pandas** for DataFrame transforms, joins, and aggregations.
Fallback: **Legacy Python / openpyxl / helper scripts** only when officecli or pandas does not cover the requirement.
Do NOT use this skill for Word, HTML dashboards, or external database orchestration.

---

## Tool Discovery

Always confirm syntax first:

```bash
officecli --help
officecli xlsx add
officecli xlsx set
officecli xlsx query --help
officecli import --help
```

Drill into a specific object when needed:

```bash
officecli xlsx add table
officecli xlsx add validation
officecli xlsx set cell
officecli xlsx set chart
```

---

## Quick Decision

| Task | Tool | Command | Notes |
|------|------|---------|-------|
| Create workbook | officecli | `officecli create model.xlsx` | Blank workbook first |
| Add worksheet | officecli | `officecli add model.xlsx / --type sheet --prop name=Inputs` | Workbook root is `/` |
| Add/edit cell | officecli | `officecli set model.xlsx /Inputs/B2 --prop value=12500 --prop type=number` | Primary mutation path |
| Read workbook | officecli | `officecli view model.xlsx text` | `text`, `annotated`, `outline`, `stats`, `issues`, `html` |
| Query cells/tables | officecli | `officecli query model.xlsx 'cell:contains("Revenue")'` | Prefer tested selectors |
| Batch workbook edits | officecli | `officecli batch model.xlsx --commands '[...]'` | Correct JSON uses `command`, not `action` |
| Resident workflow | officecli | `officecli open model.xlsx` | Still pass file path on later commands |
| CSV/TSV import | officecli | `officecli import model.xlsx /Data data.csv --header` | Simpler than manual loops |
| Add table / validation / chart | officecli | `officecli add model.xlsx /Data --type table --prop ref=A1:D10` | Native structured workbook objects |
| Data transformation | pandas | `pd.read_excel(...)` → transform → write workbook | Not legacy; pandas is primary for analysis |
| Formula recalculation | Fallback helper | `python scripts/recalc.py output.xlsx` | officecli does not recalculate |
| CJK width/font handling | Legacy Python fallback | `scripts/ooxml/cjk_utils.py` | Excel native CJK work is deferred to Phase 08 |

---

## Core Command Model

Runtime syntax is file-first:

```bash
officecli view FILE MODE
officecli add FILE PARENT --type TYPE --prop key=value
officecli set FILE PATH --prop key=value
officecli query FILE "selector"
officecli batch FILE --commands '[{"command":"set",...}]'
officecli open FILE
officecli close FILE
officecli import FILE /Sheet source.csv --header
```

### PATH Syntax

```text
/{SheetName}/A1             # single cell
/{SheetName}/A1:D10         # range
/{SheetName}/row[3]         # row by number
/{SheetName}/col[B]         # column by letter
/{SheetName}/table[1]       # table by index
/{SheetName}/chart[1]       # chart by index
/{SheetName}/validation[1]  # validation rule by index
/{SheetName}/comment[1]     # comment by index
/{SheetName}/cf[1]          # conditional formatting entry
/namedrange[1]              # named range by index
/                           # workbook root
```

Native Excel aliases such as `Sheet1!A1` are accepted, but the skill standard stays with `/{SheetName}/A1`.

---

## Common officecli Workflows

### Create a workbook and seed the first sheet

```bash
officecli create model.xlsx
officecli add model.xlsx / --type sheet --prop name=Inputs
officecli add model.xlsx /Inputs --type cell --prop ref=A1 --prop value=Revenue
officecli set model.xlsx /Inputs/B1 --prop value=12500 --prop type=number
officecli set model.xlsx /Inputs/A1:B1 --prop bold=true --prop fill=4472C4 --prop font.color=FFFFFF
```

### Structured workbook objects

```bash
officecli add model.xlsx /Inputs --type table --prop ref=A1:B10 --prop name=InputTable
officecli add model.xlsx /Inputs --type validation --prop sqref=C2:C100 --prop type=list --prop formula1="Base,Bull,Bear"
officecli add model.xlsx /Inputs --type comment --prop ref=B1 --prop text="Source: FY2025 guidance"
officecli add model.xlsx / --type namedrange --prop name=revenue_growth --prop ref="Inputs!B2"
```

### Read and query

```bash
officecli view model.xlsx text
officecli view model.xlsx outline
officecli view model.xlsx stats
officecli view model.xlsx annotated
officecli view model.xlsx issues
officecli query model.xlsx 'cell:contains("Revenue")'
officecli query model.xlsx 'Sheet2!cell[formula=true]'
officecli query model.xlsx 'table'
```

### CSV / TSV import

```bash
officecli add model.xlsx / --type sheet --prop name=Data
officecli import model.xlsx /Data data.csv --header
officecli add model.xlsx /Data --type table --prop ref=A1:F100 --prop name=RawData
officecli set model.xlsx /Data/row[1] --prop height=22
```

---

## Batch Mode

Correct batch JSON uses `command`, `parent`/`path`, `type`, and `props`.

```bash
officecli batch model.xlsx --commands '[
  {
    "command": "set",
    "path": "/Inputs/A1",
    "props": {"value": "Revenue", "bold": true, "fill": "4472C4", "font.color": "FFFFFF"}
  },
  {
    "command": "set",
    "path": "/Inputs/B1",
    "props": {"value": 12500, "type": "number", "numFmt": "#,##0"}
  },
  {
    "command": "add",
    "parent": "/Inputs",
    "type": "validation",
    "props": {"sqref": "C2:C100", "type": "list", "formula1": "Base,Bull,Bear"}
  }
]'
```

---

## Query Mode

Use selectors that map cleanly to help output and real behavior.

```bash
officecli query model.xlsx 'cell:contains("Revenue")'
officecli query model.xlsx 'cell[font.bold=true]'
officecli query model.xlsx 'Sheet2!cell[formula=true]'
officecli query model.xlsx 'comment'
officecli query model.xlsx 'pivottable'
```

---

## Resident Mode (open / close)

Resident mode keeps the workbook cached, but commands still include the file path.

```bash
officecli open model.xlsx
officecli set model.xlsx /Inputs/A3 --prop value=Resident
officecli set model.xlsx /Inputs/B3 --prop value=9000 --prop type=number
officecli close model.xlsx
```

Use resident mode for exploratory editing. Use batch when the command list is already known.

---

## Financial Model Conventions

### Color coding

| Color | Meaning | officecli example |
|------|---------|-------------------|
| Blue `0000FF` | Hard-coded inputs | `officecli set model.xlsx /Inputs/B2:B20 --prop font.color=0000FF` |
| Black `000000` | Formula cells | `officecli set model.xlsx /Calc/B2:B50 --prop font.color=000000` |
| Green `008000` | Cross-sheet pulls | `officecli set model.xlsx /Calc/C2:C50 --prop font.color=008000` |
| Red `FF0000` | External links / broken assumptions | `officecli set model.xlsx /Audit/B2:B10 --prop font.color=FF0000` |

### Number formatting

```bash
officecli set model.xlsx /Outputs/B2:B20 --prop numFmt='$#,##0;($#,##0);-'
officecli set model.xlsx /Outputs/C2:C20 --prop numFmt='0.0%'
officecli set model.xlsx /Outputs/D2:D20 --prop numFmt='0.0x'
```

### Korean financial formats

```bash
officecli set model.xlsx /Sheet1/B2 --prop numFmt='#,##0'
officecli set model.xlsx /Sheet1/B3 --prop numFmt='#,##0,,"억"'
officecli set model.xlsx /Sheet1/B4 --prop numFmt='#,##0,"백만"'
```

### 3-sheet separation principle

- `Inputs`: blue text, user-editable assumptions
- `Calculations`: formulas only, minimal formatting noise
- `Outputs`: charts, summaries, management-facing views

### Hard-coded source documentation

```bash
officecli set model.xlsx /Inputs/B1 --prop value=0.15 --prop type=number
officecli add model.xlsx /Inputs --type comment --prop ref=B1 --prop text='Source: Company 10-K FY2025 p.45'
```

### Never hardcode calculations in agent code

```bash
officecli set model.xlsx /Calc/B10 --prop formula='=SUM(B2:B9)'
officecli set model.xlsx /Calc/C5 --prop formula='=(C4-C2)/C2'
```

The workbook must remain recalculable when inputs change.

---

## Formula Recalculation

**Critical:** officecli writes formulas but does **not** recalculate them.
Always run a recalc pass after formula generation.

```bash
python scripts/recalc.py output.xlsx
# or
soffice --headless --calc --convert-to xlsx output.xlsx
```

### Recalc checklist

- [ ] Sample formulas use correct sheet/range references
- [ ] No off-by-one row mapping mistakes
- [ ] No circular references
- [ ] `recalc.py` returns success with zero errors
- [ ] Final cached values match expected outputs

---

## Pandas DataFrame → Excel Pipeline

pandas is **not** legacy here. It is the primary analysis layer for transformations that officecli should not reimplement.

### When pandas is the right tool

- groupby / pivot_table / merge / melt / rolling work
- multi-source joins
- data cleaning before workbook writeback
- precomputing report tables before formatting

### Basic pipeline

```python
import pandas as pd

df = pd.read_excel('input.xlsx')
summary = df.groupby('Product')['Revenue'].agg(['sum', 'mean', 'count'])

with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Raw', index=False)
    summary.to_excel(writer, sheet_name='Summary')
```

### Post-pandas formatting with officecli

```bash
officecli set output.xlsx /Raw/A1:Z1 --prop bold=true --prop fill=4472C4 --prop font.color=FFFFFF
officecli add output.xlsx /Raw --type table --prop ref=A1:Z100 --prop name=RawData
officecli set output.xlsx /Summary/B2:D10 --prop numFmt='$#,##0'
```

---

## Data Pipeline (pandas → CSV → officecli)

> **Architecture**: pandas creates the data → CSV/TSV export preserves the table cleanly →
> officecli creates/imports the workbook → officecli formats and validates.
> This path keeps pandas focused on transforms and lets officecli own the OOXML package.

### Why CSV/TSV First?

1. Declarative (one command per style) vs imperative (multiple Python API calls)
2. Scriptable in shell (composable with other CLI tools)
3. Batchable (single open/save cycle for all formatting)
4. Owned end-to-end by officecli, so `officecli validate` stays aligned

### Quick Pipeline: Single Sheet

```python
import pandas as pd

df = pd.DataFrame({
    "제품명": ["김치냉장고", "에어컨", "세탁기", "건조기"],
    "매출액": [15000000, 23000000, 18000000, 12000000],
    "전년비": [1.25, 1.15, 0.95, 1.30],
    "카테고리": ["가전", "가전", "가전", "가전"],
})
df.to_csv("sales_report.csv", index=False)
```

```bash
officecli create sales_report.xlsx
officecli import sales_report.xlsx /Sheet1 sales_report.csv --header

officecli batch sales_report.xlsx --commands '[
  {"command":"set","path":"/Sheet1/A1:D1","props":{"font.bold":"true","font.size":"12","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/Sheet1/B2:B5","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/Sheet1/C2:C5","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/Sheet1/col[A]","props":{"width":"18"}},
  {"command":"set","path":"/Sheet1/col[B]","props":{"width":"15"}},
  {"command":"set","path":"/Sheet1","props":{"freeze":"A2"}}
]'
officecli validate sales_report.xlsx
```

### Conditional Formatting

```bash
# Data bars
officecli add f.xlsx '/Sheet1' --type databar --prop range=B2:B5 --prop color=4472C4

# Color scale (heatmap)
officecli add f.xlsx '/Sheet1' --type colorscale --prop range=C2:C5

# Icon sets (traffic lights)
officecli add f.xlsx '/Sheet1' --type iconset --prop range=C2:C5

# Formula-based: highlight declining rows
officecli add f.xlsx '/Sheet1' --type formulacf \
  --prop range=C2:C5 --prop formula='$C2<1' --prop fill=FF6B6B
```

### Charts

```bash
officecli add f.xlsx '/Sheet1' --type chart \
  --prop chartType=bar --prop dataRange="Sheet1!A1:B5" \
  --prop title="제품별 매출액" --prop width=10 --prop height=15

officecli add f.xlsx '/Sheet1' --type chart \
  --prop chartType=pie \
  --prop categories="김치냉장고,에어컨,세탁기,건조기" \
  --prop data="Sales:15000000,23000000,18000000,12000000" \
  --prop title="매출 비중" --prop dataLabels=true
```

### Multi-Sheet Reports

```python
df_sales.to_csv("sales.csv", index=False)
df_costs.to_csv("costs.csv", index=False)
df_summary.to_csv("summary.csv", index=False)
```

```bash
officecli create quarterly_report.xlsx
officecli add quarterly_report.xlsx / --type sheet --prop name="매출"
officecli add quarterly_report.xlsx / --type sheet --prop name="비용"
officecli add quarterly_report.xlsx / --type sheet --prop name="요약"
officecli import quarterly_report.xlsx /매출 sales.csv --header
officecli import quarterly_report.xlsx /비용 costs.csv --header
officecli import quarterly_report.xlsx /요약 summary.csv --header

officecli batch quarterly_report.xlsx --commands '[
  {"command":"set","path":"/매출/A1:C1","props":{"font.bold":"true","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/매출/B2:C4","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/매출","props":{"freeze":"A2"}},
  {"command":"set","path":"/비용/A1:C1","props":{"font.bold":"true","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/비용/B2:B5","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/비용/C2:C5","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/요약/A1:B1","props":{"font.bold":"true","font.name":"Malgun Gothic"}}
]'
```

### CSV Import Pipeline (No Python)

```bash
officecli create report.xlsx
officecli import report.xlsx /Sheet1 data.csv --header
officecli set report.xlsx '/Sheet1/A1:D1' --prop font.bold=true --prop font.name="Malgun Gothic"
officecli add report.xlsx /Sheet1 --type autofilter --prop range=A1:D1
officecli validate report.xlsx
```

TSV and stdin are also supported:

```bash
officecli import report.xlsx /Sheet1 data.tsv --format tsv --header
cat query_results.csv | officecli import report.xlsx /Sheet1 --stdin --header
```

### Number Format Reference

| Format Code | Example Output | Use Case |
|------------|----------------|----------|
| `#,##0` | 15,000,000 | Integer with comma separators |
| `#,##0.00` | 15,000,000.00 | Currency (2 decimals) |
| `0.0%` | 125.0% | Percentage (1 decimal) |
| `yyyy-mm-dd` | 2026-03-27 | ISO date |
| `yyyy"년" mm"월" dd"일"` | 2026년 03월 27일 | Korean date |
| `₩#,##0` | ₩15,000,000 | KRW currency |
| `¥#,##0` | ¥15,000,000 | JPY/CNY currency |

### End-to-End Pipeline Script

```bash
#!/bin/bash
set -euo pipefail
OUTPUT="monthly_sales_$(date +%Y%m).xlsx"

python3 -c "
import pandas as pd, random
months = ['1월','2월','3월','4월','5월','6월']
products = ['김치냉장고','에어컨','세탁기','건조기','식기세척기']
rows = [{'제품명': p, '월': m, '매출액': random.randint(8000000, 30000000), '성장률': round(random.uniform(0.85, 1.35), 2)} for p in products for m in months]
pd.DataFrame(rows).to_csv('monthly_sales.csv', index=False)
"

officecli create "$OUTPUT"
officecli add "$OUTPUT" / --type sheet --prop name="월별매출"
officecli import "$OUTPUT" /월별매출 monthly_sales.csv --header

officecli batch "$OUTPUT" --commands '[
  {"command":"set","path":"/월별매출/A1:D1","props":{"font.bold":"true","font.size":"11","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/월별매출/C2:C31","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/월별매출/D2:D31","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/월별매출","props":{"freeze":"A2"}},
  {"command":"add","path":"/월별매출","type":"autofilter","props":{"range":"A1:D1"}},
  {"command":"add","path":"/월별매출","type":"databar","props":{"range":"C2:C31","color":"4472C4"}},
  {"command":"add","path":"/월별매출","type":"formulacf","props":{"range":"D2:D31","formula":"$D2<1","fill":"FF6B6B"}}
]'

officecli validate "$OUTPUT"
```

### Pipeline Validation Checklist

- [ ] `officecli validate` passes with no errors
- [ ] Row count matches DataFrame length + 1 (header)
- [ ] CJK text displays correctly in `view text`
- [ ] Number formats show commas/percentages as expected
- [ ] Conditional formatting highlights correct cells
- [ ] Charts reference correct data ranges

### Pipeline Quick Reference

| Task | Command |
|------|---------|
| Import CSV | `officecli import f.xlsx /Sheet1 data.csv --header` |
| Header styling | `officecli set f.xlsx '/Sheet1/A1:D1' --prop font.bold=true --prop font.name="Malgun Gothic"` |
| Number format | `officecli set f.xlsx '/Sheet1/B2:B99' --prop numFmt="#,##0"` |
| Column width | `officecli set f.xlsx '/Sheet1/col[A]' --prop width=18` |
| Freeze pane | `officecli set f.xlsx /Sheet1 --prop freeze=A2` |
| Data bar | `officecli add f.xlsx /Sheet1 --type databar --prop range=B2:B99` |
| Highlight rule | `officecli add f.xlsx /Sheet1 --type formulacf --prop range=... --prop formula=...` |
| Chart | `officecli add f.xlsx /Sheet1 --type chart --prop chartType=bar --prop dataRange=...` |
| Autofilter | `officecli add f.xlsx /Sheet1 --type autofilter --prop range=A1:D1` |
| Batch format | `officecli batch f.xlsx --commands '[...]'` |

---

## CJK / Korean Text Handling

> CJK 상세 규칙 → see `references/officecli-cjk.md`

> **Phase 08 scope:** Excel-specific CJK width/font handling in officecli is deferred. This is not a Phase 04 failure.

### Cell Fonts vs Chart Fonts

Excel has separate font systems for cell content and chart text:
- **Cell fonts**: set via `--prop font.name="Malgun Gothic"` on cell ranges
- **Chart fonts**: set via chart `--prop font="Malgun Gothic"` or chart title props
- Column widths need CJK-aware calculation (Korean/Chinese characters are ~2× Latin width)

```bash
# Cell CJK font
officecli set data.xlsx '/Sheet1/A1:C1' --prop font.name="Malgun Gothic" --prop font.bold=true

# Korean column headers
officecli set data.xlsx /Sheet1/A1 --prop value="제품명"
officecli set data.xlsx /Sheet1/B1 --prop value="매출액"
officecli set data.xlsx /Sheet1/C1 --prop value="전년비"

# Wider columns for CJK text
officecli set data.xlsx '/Sheet1/col[A]' --prop width=18
```

### Current fallback

Use the existing helper when Korean text width or column-fit matters:

```bash
python scripts/ooxml/cjk_utils.py report.xlsx
```

---

## Accessibility (WCAG 2.1 AA)

> 접근성 기준 → see `references/officecli-accessibility.md`

```bash
officecli add model.xlsx / --type sheet --prop name='Revenue Summary'
officecli view model.xlsx issues
```

### Table Structure

- Every table must have a header row: `officecli add f.xlsx /Sheet1 --type table --prop ref=A1:D10`
- Named ranges improve navigation for screen readers: `officecli add f.xlsx / --type namedrange --prop name=revenue --prop ref="Sheet1!B2"`
- Avoid merged cells — they confuse screen readers and assistive technology

### Accessibility checklist

- [ ] Sheet names are descriptive (not "Sheet1")
- [ ] Charts have useful titles
- [ ] Color contrast is readable (≥ 4.5:1 normal text)
- [ ] Body text stays at readable size (≥ 12pt)
- [ ] Header rows are clear in tables
- [ ] Korean text is visible without `###` truncation
- [ ] Information not conveyed by color alone
- [ ] Named ranges used for key data areas

When editing existing workbooks, preserve layout, validations, names, and formulas unless explicitly asked to change them.

```bash
officecli view template.xlsx outline
officecli get template.xlsx /
officecli set template.xlsx /Sheet1/B5 --prop value='ABC Corp'
officecli set template.xlsx /Sheet1/C10 --prop value=42000 --prop type=number
```

### Rules

- Never drop `DefinedName` entries without checking formulas/charts first
- Never strip existing validation or conditional formatting accidentally
- Never save `data_only=True` workbooks back over formula models
- Extend tables/charts intentionally, not by accident

---

## QA Verification

```bash
officecli view output.xlsx outline
officecli view output.xlsx issues
officecli validate output.xlsx
officecli view output.xlsx annotated
python scripts/recalc.py output.xlsx
soffice --headless --convert-to pdf output.xlsx
```

### QA checklist

- [ ] No `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`
- [ ] Formula recalculation finished successfully
- [ ] Named ranges still point at intended cells
- [ ] Validation lists still work
- [ ] Conditional formatting still matches the business rule
- [ ] Financial color conventions remain intact

---

## Legacy Python CLI (Fallback)

| Command | Role | Status |
|---------|------|--------|
| `python scripts/xlsx_cli.py validate input.xlsx --json` | Workbook validation helper | Fallback |
| `python scripts/xlsx_cli.py formula-audit input.xlsx --json` | Formula audit | Fallback |
| `python scripts/recalc.py output.xlsx` | Formula recalculation | Required fallback |
| `python scripts/soffice.py convert output.xlsx output.pdf` | PDF conversion | Fallback |
| `python scripts/ooxml/unpack.py file.xlsx unpacked/` | Zip-level OOXML surgery | Legacy |
| `python scripts/ooxml/pack.py unpacked/ fixed.xlsx` | Repack OOXML | Legacy |

---

## Dependencies

| Tool | Why it exists | Status |
|------|---------------|--------|
| `~/.local/bin/officecli` | Primary Excel CLI | Required |
| `pandas` | DataFrame analysis pipeline | Primary for transforms |
| `openpyxl` | pandas Excel engine + fallback editing | Fallback support |
| `python3` | Helper scripts | Optional fallback |
| `soffice` | Recalculation / PDF export | Optional fallback |
| `alasql` + `xlsx` | Optional SQL-style workbook querying | Optional |
| `scripts/ooxml/cjk_utils.py` | Excel CJK width/font fallback | Deferred until Phase 08 replacement |
