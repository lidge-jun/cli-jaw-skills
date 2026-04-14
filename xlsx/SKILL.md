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

## Quick Reference

| Task | Action |
|------|--------|
| Read / analyze content | Use `view` and `get` commands below |
| Edit existing workbook | Read [editing.md](./editing.md) |
| Create from scratch | Read [creating.md](./creating.md) |

### Quick Decision

| Task | Tool | Command | Notes |
|------|------|---------|-------|
| Create workbook | officecli | `officecli create model.xlsx` | Blank workbook first |
| Add worksheet | officecli | `officecli add model.xlsx / --type sheet --prop name=Inputs` | Workbook root is `/` |
| Add/edit cell | officecli | `officecli set model.xlsx /Inputs/B2 --prop value=12500 --prop type=number` | Primary mutation path |
| Read workbook | officecli | `officecli view model.xlsx text` | `text`, `annotated`, `outline`, `stats`, `issues`, `html` |
| Query cells/tables | officecli | `officecli query model.xlsx 'cell:contains("Revenue")'` | Prefer tested selectors |
| Batch workbook edits | officecli | `officecli batch model.xlsx --commands '[...]'` | JSON uses `command`, not `action` |
| Resident workflow | officecli | `officecli open model.xlsx` | Still pass file path on later commands |
| CSV/TSV import | officecli | `officecli import model.xlsx /Data data.csv --header` | TSV: `--format tsv`; stdin: `--stdin` |
| Add table / validation / chart | officecli | `officecli add model.xlsx /Data --type table --prop ref=A1:D10` | Native structured workbook objects |
| Data transformation | pandas | `pd.read_excel(...)` -> transform -> write | pandas is PRIMARY for analysis |
| Formula recalculation | Fallback helper | `python3 scripts/recalc.py output.xlsx` | officecli does not recalculate |

---

## Subskill References

Read **only** the subskill relevant to the current task. Do not preload all.

| Subskill | Path (relative) | When to read |
|----------|-----------------|--------------|
| **officecli-financial-model** | `./officecli-financial-model/SKILL.md` | 3-statement models, DCF, LBO, revenue builds, assumption sheets |
| **officecli-data-dashboard** | `./officecli-data-dashboard/SKILL.md` | Charts, pivot tables, conditional formatting, dashboard layouts |
| **creating.md** | `./creating.md` | Detailed recipes for building workbooks from scratch |
| **editing.md** | `./editing.md` | Modification guides for existing workbooks |

---

## Design Principles for Spreadsheets

**Professional spreadsheets need clear structure, correct formulas, and intentional formatting.**

### Alignment

- Numbers = **right-aligned** (default in Excel; do not override)
- Labels / text = **left-aligned**
- Headers = **center or left**, bold, with fill color

### Color Coding Convention

| Color | Hex | Meaning | Example |
|-------|-----|---------|---------|
| Blue | `0000FF` | Hard-coded inputs | User-editable assumptions |
| Black | `000000` | Formula cells | Calculations, references |
| Green | `008000` | Cross-sheet output pulls | Summary / output values |
| Red | `FF0000` | Warning / negative values | Broken assumptions, losses |

Apply via: `officecli set model.xlsx /Inputs/B2:B20 --prop font.color=0000FF`

### 3-Sheet Separation

| Sheet | Purpose | Text color |
|-------|---------|------------|
| **Inputs** | User-editable assumptions | Blue |
| **Model** (or Calculations) | Formulas only, minimal formatting noise | Black |
| **Outputs** | Charts, summaries, management-facing views | Green for pulled values |

### Source Annotations

Every hard-coded input cell MUST have a comment documenting its origin:

```bash
officecli add model.xlsx /Inputs --type comment \
  --prop ref=B1 --prop text='Source: Company 10-K FY2025 p.45'
```

### Use Formulas, Not Hardcoded Values (MANDATORY)

The spreadsheet must remain dynamic -- when source data changes, formulas recalculate automatically. Hardcoded values break this contract.

```bash
# WRONG -- hardcoded calculation result
officecli set data.xlsx "/Sheet1/B10" --prop value=5000

# CORRECT -- let Excel calculate
officecli set data.xlsx "/Sheet1/B10" --prop formula="SUM(B2:B9)"
```

---

## Mandatory Verification (NEVER SKIP)

After ANY XLSX edit, ALWAYS execute both steps:

```bash
# Step 1: structural validation
officecli validate output.xlsx

# Step 2: visual PDF proof
soffice --headless --convert-to pdf --outdir /tmp output.xlsx
# Check: formula results, cell formatting, chart rendering, merged cells
```

Skip neither step. `validate` catches structural errors; the PDF catches rendering issues (truncated CJK, broken charts, invisible text).

---

## Tool Discovery

**When unsure about property names, value formats, or command syntax, run help instead of guessing.** One help query is faster than guess-fail-retry loops.

```bash
officecli xlsx set              # All settable elements and their properties
officecli xlsx set cell         # Cell properties in detail
officecli xlsx set cell.font    # Specific property format and examples
officecli xlsx add              # All addable element types
officecli xlsx view             # All view modes
officecli xlsx get              # All navigable paths
officecli xlsx query            # Query selector syntax
```

---

## Core Workflows

### Execution Model

**Run commands one at a time. Do not write all commands into a shell script and execute it as a single block.**

OfficeCLI is incremental: every `add`, `set`, and `remove` immediately modifies the file and returns output. Use this to catch errors early:

1. **One command at a time, then read the output.** Check the exit code before proceeding.
2. **Non-zero exit = stop and fix immediately.** Do not continue building on a broken state.
3. **Verify after structural operations.** After adding a sheet, chart, pivot table, or named range, run `get` or `validate` before building on top of it.

### Reading & Analyzing

```bash
officecli view data.xlsx text                              # Plain text dump
officecli view data.xlsx text --start 1 --end 50 --cols A,B,C  # Filtered
officecli view data.xlsx outline                           # Structure overview
officecli view data.xlsx annotated                         # Type/formula annotations
officecli view data.xlsx stats                             # Summary statistics
officecli view data.xlsx issues                            # Empty sheets, broken formulas
```

### Element Inspection (PATH Syntax)

```bash
officecli get data.xlsx /                       # Workbook root (all sheets, doc props)
officecli get data.xlsx "/Sheet1"               # Sheet overview
officecli get data.xlsx "/Sheet1/A1"            # Single cell (value, type, formula, font, fill)
officecli get data.xlsx "/Sheet1/A1:D10"        # Cell range
officecli get data.xlsx "/Sheet1/row[1]"        # Row properties
officecli get data.xlsx "/Sheet1/col[A]"        # Column properties
officecli get data.xlsx "/Sheet1/chart[1]"      # Chart
officecli get data.xlsx "/Sheet1/table[1]"      # Table (ListObject)
officecli get data.xlsx "/Sheet1/validation[1]" # Data validation rule
officecli get data.xlsx "/Sheet1/cf[1]"         # Conditional formatting rule
officecli get data.xlsx "/Sheet1/comment[1]"    # Comment
officecli get data.xlsx "/namedrange[1]"        # Named range
```

Add `--depth N` to expand children, `--json` for structured output. Excel-native notation also supported: `Sheet1!A1`, `Sheet1!A1:D10`.

### CSS-like Queries

```bash
officecli query data.xlsx 'cell:has(formula)'           # Cells with formulas
officecli query data.xlsx 'cell:contains("Revenue")'    # Cells containing text
officecli query data.xlsx 'cell:empty'                  # Empty cells
officecli query data.xlsx 'cell[type=Number]'           # Cells by type
officecli query data.xlsx 'cell[font.bold=true]'        # Cells by formatting
officecli query data.xlsx 'B[value!=0]'                 # Column B non-zero
officecli query data.xlsx 'Sheet1!cell[value="100"]'    # Sheet-scoped
officecli query data.xlsx 'chart'                       # Find all charts
officecli query data.xlsx 'table'                       # Find all tables
officecli query data.xlsx 'pivottable'                  # Find all pivot tables
```

Operators: `=`, `!=`, `~=` (contains), `>=`, `<=`, `[attr]` (exists).

### Cell Formatting

```bash
# Column width (character units, ~1 char = 7px) -- no auto-fit available
officecli set data.xlsx "/Sheet1/col[A]" --prop width=15

# Row height (points)
officecli set data.xlsx "/Sheet1/row[1]" --prop height=20

# Freeze panes (headers)
officecli set data.xlsx "/Sheet1" --prop freeze=A2

# Print area
officecli set data.xlsx "/Sheet1" --prop printArea="A1:F20"
```

Common widths: labels=20-25, numbers=12-15, dates=12, short codes=8-10.

### Data Validation

```bash
# Dropdown list
officecli add data.xlsx /Sheet1 --type validation \
  --prop sqref="C2:C100" --prop type=list \
  --prop formula1="Yes,No,Maybe" --prop showError=true

# Number range
officecli add data.xlsx /Sheet1 --type validation \
  --prop sqref="D2:D100" --prop type=decimal \
  --prop operator=between --prop formula1=0 --prop formula2=100
```

### Batch Mode

```bash
cat <<'EOF' | officecli batch data.xlsx
[
  {"command":"set","path":"/Sheet1/A1","props":{"value":"Revenue","bold":"true","fill":"1F4E79","font.color":"FFFFFF"}},
  {"command":"set","path":"/Sheet1/B1","props":{"value":"Q1","bold":"true","fill":"1F4E79","font.color":"FFFFFF"}}
]
EOF
```

Batch supports: `add`, `set`, `get`, `query`, `remove`, `move`, `swap`, `view`, `raw`, `raw-set`, `validate`.
Batch fields: `command`, `path`, `parent`, `type`, `from`, `to`, `index`, `after`, `before`, `props` (dict), `selector`, `mode`, `depth`, `part`, `xpath`, `action`, `xml`.

### Resident Mode

```bash
officecli open data.xlsx        # Load once into memory
officecli add data.xlsx ...     # All commands run in memory -- fast
officecli set data.xlsx ...
officecli close data.xlsx       # Write once to disk
```

### CSV / TSV Import

```bash
officecli import f.xlsx /Sheet1 data.csv --header           # CSV
officecli import f.xlsx /Sheet1 data.tsv --header --format tsv  # TSV
cat data.csv | officecli import f.xlsx /Sheet1 --stdin --header  # stdin
```

---

## pandas Pipeline

**pandas is the PRIMARY analysis layer, NOT legacy.** It is the first-choice tool for data transforms that officecli should not reimplement.

| Use pandas when | Use officecli when |
|---|---|
| groupby, pivot_table, merge, melt, rolling | Cell-level mutation, formatting, styling |
| Multi-source joins and aggregations | Chart creation and configuration |
| Data cleaning before workbook writeback | Validation rules, conditional formatting |
| Precomputing report tables | Workbook structure (sheets, tables, named ranges) |

### Standard Flow: pandas -> CSV -> officecli

```
pandas DataFrame
    |  .to_csv("data.csv", index=False)
    v
officecli create output.xlsx
officecli import output.xlsx /Sheet1 data.csv --header
officecli batch output.xlsx --commands '[formatting...]'
officecli validate output.xlsx
```

This path keeps pandas focused on transforms and lets officecli own the OOXML package. One `import` command replaces dozens of `set cell` calls.

---

## Formula Recalculation (CRITICAL)

**officecli writes formulas but does NOT recalculate them.**
Always run a recalc pass after formula generation.

```bash
python3 scripts/recalc.py output.xlsx
# or
soffice --headless --calc --convert-to xlsx output.xlsx
```

### Recalc Checklist

- [ ] Sample formulas use correct sheet/range references
- [ ] No off-by-one row mapping mistakes
- [ ] No circular references
- [ ] `recalc.py` returns success with zero errors
- [ ] Final cached values match expected outputs

---

## Number Format Reference

### Standard Formats

| Type | Format String | Example Output | Code |
|------|--------------|----------------|------|
| Currency | `$#,##0` | $1,234 | `--prop numFmt='$#,##0'` |
| Currency (neg parens) | `$#,##0;($#,##0);"-"` | ($1,234) | `--prop numFmt='$#,##0;($#,##0);"-"'` |
| Percentage | `0.0%` | 12.5% | `--prop numFmt="0.0%"` |
| Decimal | `#,##0.00` | 1,234.56 | `--prop numFmt="#,##0.00"` |
| Accounting | `_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)` | $ 1,234 | (use batch heredoc) |
| Date | `yyyy-mm-dd` | 2026-03-27 | `--prop numFmt="yyyy-mm-dd"` |
| Date (long) | `mmmm d, yyyy` | March 27, 2026 | `--prop numFmt="mmmm d, yyyy"` |
| Year as text | `@` | 2026 (not 2,026) | `--prop type=string` |
| Multiples | `0.0x` | 12.5x | `--prop numFmt="0.0x"` |
| Zeros as dash | `#,##0;-#,##0;"-"` | - | `--prop numFmt='#,##0;-#,##0;"-"'` |

### Korean Number Formats

| Format Code | Example Output | Use Case |
|------------|----------------|----------|
| `#,##0` | 15,000,000 | Integer with 1000 comma separators |
| `₩#,##0` | ₩15,000,000 | KRW currency |
| `#,##0,,"억"` | 150억 | Hundred-million unit |
| `#,##0,"백만"` | 15백만 | Million unit |
| `0.0%` | 125.0% | Percentage (1 decimal) |

**Shell quoting:** Number formats containing `$` must use single quotes (`'$#,##0'`) or heredoc in batch mode. Double quotes cause shell variable expansion.

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|-----------------|
| `--name "foo"` | Use `--prop name="foo"` -- all attributes go through `--prop` |
| Guessing property names | Run `officecli xlsx set cell` to see exact names |
| `\n` in shell strings | Use `\\n` for newlines in `--prop text="line1\\nline2"` |
| Modifying an open file | Close the file in Excel first |
| Hex colors with `#` | Use `FF0000` not `#FF0000` -- no hash prefix |
| Paths are 1-based | `"/Sheet1/row[1]"`, `"/Sheet1/col[1]"` -- XPath convention |
| `--index` is 0-based | `--index 0` = first position -- array convention |
| Unquoted `[N]` in zsh/bash | Shell glob-expands `/Sheet1/row[1]` -- always quote paths |
| Sheet names with spaces | Quote the full path: `"/My Sheet/A1"` |
| Formula prefix `=` | OfficeCLI strips the `=` -- use `formula="SUM(A1:A10)"` not `formula="=SUM(A1:A10)"` |
| Cross-sheet `!` in formulas | Use batch/heredoc for cross-sheet formulas. NEVER use single quotes for formulas containing `!`. Verify with `officecli get` that formula shows `Sheet1!A1` (no backslash). |
| Hardcoded calculated values | Use `--prop formula="SUM(B2:B9)"` not `--prop value=5000` |
| `$` and `'` in batch JSON | Use heredoc: `cat <<'EOF' \| officecli batch` -- single-quoted delimiter prevents shell expansion |
| Number format with `$` | Shell interprets `$` -- use single quotes: `numFmt='$#,##0'` |
| Year displayed as "2,026" | Set cell type to string: `--prop type=string` or use `numFmt="@"` |
| Sheet names containing `!` | Excel uses `!` as sheet-range delimiter. Use only alphanumeric, spaces, hyphens, underscores. |

### Formula Verification Checklist

- [ ] Test 2-3 sample cell references: verify they pull correct values
- [ ] Column mapping: confirm cell references point to intended columns
- [ ] Row offsets: check formula ranges include all data rows
- [ ] Division by zero: verify denominators are non-zero or wrapped in IFERROR
- [ ] Cross-sheet references: use correct `Sheet1!A1` format
- [ ] Cross-sheet formula escaping: run `officecli get` on 2-3 cross-sheet formula cells -- confirm no `\!` in the formula string
- [ ] Named ranges: verify `ref` values match actual data locations
- [ ] Edge cases: test with zero values, negative numbers, empty cells
- [ ] Chart data vs formula results: verify each chart data point matches the source cell

### Pre-Delivery Checklist

- [ ] Metadata set (title, author)
- [ ] All formula cells contain formulas (not hardcoded values)
- [ ] No formula error values (#REF!, #DIV/0!, #VALUE!, #NAME?, #N/A)
- [ ] Number formats applied (currency, percentage, dates)
- [ ] Column widths set explicitly (no default 8.43)
- [ ] Header row styled (bold, fill, freeze panes)
- [ ] Data validation on input cells
- [ ] Charts have titles and readable axis labels
- [ ] Chart data matches source cells (prefer cell-range refs over inline data)
- [ ] Named ranges defined for key assumptions
- [ ] Document validates with `officecli validate`
- [ ] No placeholder text remaining
- [ ] Comments on hardcoded assumption values documenting their source

### QA Error Scan

Approach QA as a bug hunt, not a confirmation step. If you found zero issues on first inspection, you were not looking hard enough.

```bash
officecli view data.xlsx issues                         # Broken formulas, missing refs
officecli query data.xlsx 'cell:has(formula)'           # Verify formulas exist
officecli query data.xlsx 'cell:contains("#REF!")'      # Formula error scan
officecli query data.xlsx 'cell:contains("#DIV/0!")'
officecli query data.xlsx 'cell:contains("#VALUE!")'
officecli query data.xlsx 'cell:contains("#NAME?")'
officecli query data.xlsx 'cell:contains("#N/A")'
officecli validate data.xlsx                            # Structural validation
```

### Verification Loop

1. Generate workbook
2. Run `view issues` + `view annotated` (sample ranges) + `validate`
3. Run formula error queries (all 5 error types)
4. List issues found (if none found, look again more critically)
5. Fix issues
6. Re-verify affected areas -- one fix often creates another problem
7. Repeat until a full pass reveals no new issues

**Do not declare success until you have completed at least one fix-and-verify cycle.**

---

## Anti-Patterns (NEVER DO)

**Formula results hardcoded as values -- STRICTLY FORBIDDEN.** The workbook must remain recalculable when inputs change.

**Fictional example data leaking into output -- FORBIDDEN.** Never use placeholder names in deliverable workbooks.

**Merged cell abuse -- FORBIDDEN.** Merged cells break sorting, filtering, screen readers, and programmatic access. Use center-across-selection or column width adjustments instead. Exception: a single title row.

**Sheet names containing `!` -- ESCAPE WARNING.** Excel uses `!` as the sheet-range delimiter.

---

## Legacy Python CLI (Fallback)

| Command | Role | Status |
|---------|------|--------|
| `python3 scripts/xlsx_cli.py validate input.xlsx --json` | Workbook validation helper | Fallback |
| `python3 scripts/xlsx_cli.py formula-audit input.xlsx --json` | Formula audit | Fallback |
| `python3 scripts/recalc.py output.xlsx` | Formula recalculation | Required fallback |
| `soffice --headless --convert-to pdf output.xlsx` | PDF conversion | Fallback |
| `officecli raw output.xlsx /xl/workbook.xml` | Raw OOXML inspection | Preferred fallback |
| `officecli raw-set output.xlsx /xl/workbook.xml ...` | Raw OOXML edit | Preferred fallback |

### Known Issues

| Issue | Workaround |
|---|---|
| Chart series cannot be added after creation | Delete and recreate with all series |
| No visual preview | Use `view text`/`annotated`/`stats`/`issues` for verification |
| Formula cached values for new formulas | Cached value updates when opened in Excel/LibreOffice |
| Batch intermittent failure | Keep batches to 8-12 ops; retry failures individually |
| Data bar default min/max invalid | Always specify explicit `--prop min=N --prop max=N` |
| Cell protection requires sheet protection | `locked` only takes effect when sheet is protected |

---

## Dependencies

| Tool | Why it exists | Status |
|------|---------------|--------|
| `~/.local/bin/officecli` | Primary Excel CLI | Required |
| `pandas` | DataFrame analysis pipeline | Primary for transforms |
| `openpyxl` | pandas Excel engine + fallback editing | Fallback support |
| `python3` | Helper scripts | Optional fallback |
| `soffice` | Recalculation / PDF export | Optional fallback |
