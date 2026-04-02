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

## CJK / Korean Text Handling

> **Phase 08 scope:** Excel-specific CJK width/font handling in officecli is deferred. This is not a Phase 04 failure.

### Current fallback

Use the existing helper when Korean text width or column-fit matters:

```python
from scripts.ooxml.cjk_utils import auto_fit_columns, get_display_width
```

```bash
python scripts/ooxml/cjk_utils.py report.xlsx
```

### Practical rule

- officecli remains primary for workbook structure and simple formatting
- CJK width tuning stays in fallback scripts until Phase 08

### Phase 05 note

> `scripts/ooxml/` helpers overlap with `officecli raw`, `officecli validate`, and workbook mutation paths. Phase 05 should consolidate the remaining duplication while leaving Excel CJK width work scheduled for Phase 08.

---

## Template Preservation

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

## Accessibility (WCAG 2.1 AA)

```bash
officecli add model.xlsx / --type sheet --prop name='Revenue Summary'
officecli view model.xlsx issues
```

### Accessibility checklist

- [ ] Sheet names are descriptive
- [ ] Charts have useful titles
- [ ] Color contrast is readable
- [ ] Body text stays at readable size
- [ ] Header rows are clear in tables
- [ ] Korean text is visible without `###` truncation

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
