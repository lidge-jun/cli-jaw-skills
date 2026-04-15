---
name: xlsx
description: "Excel XLSX create, read, edit, analyze. Triggers: Excel, .xlsx, spreadsheet, financial model, data analysis, pivot, chart."
---

# XLSX Skill

Use this skill for `.xlsx`, `.xlsm`, `.csv`, and `.tsv` work that ends in an Excel workbook.

Primary tool: **officecli** for workbook mutation and inspection.
Primary data pipeline: **pandas** for DataFrame transforms, joins, aggregations.
Fallback: **Python OOXML scripts** (`scripts/*.py`) and **openpyxl** for tasks officecli/pandas cannot cover — formula recalc, raw OOXML inspection, complex openpyxl styling. See §3.

Do NOT use this skill for Word, HTML dashboards, or external database orchestration.

---

## 1. Quick Decision

| Task | Tool | Command | Notes |
|------|------|---------|-------|
| **Format like existing workbook** | shell + officecli | `cp source.xlsx target.xlsx && officecli open target.xlsx` | **MANDATORY for "format like X" requests — see §2** |
| Create workbook | officecli | `officecli create model.xlsx` | Blank workbook first |
| Add worksheet | officecli | `officecli add model.xlsx / --type sheet --prop name=Inputs` | Workbook root is `/` |
| Add/edit cell | officecli | `officecli set model.xlsx /Inputs/B2 --prop value=12500 --prop type=number` | Primary mutation path |
| Read workbook | officecli | `officecli view model.xlsx text` | `text`, `annotated`, `outline`, `stats`, `issues`, `html` |
| Query cells/tables | officecli | `officecli query model.xlsx 'cell:contains("Revenue")'` | Prefer tested selectors |
| Batch workbook edits | officecli | `officecli batch model.xlsx --commands '[...]'` | JSON uses `command`, not `action` |
| Resident workflow | officecli | `officecli open model.xlsx` | Returns immediately; daemon in bg |
| CSV/TSV import | officecli | `officecli import model.xlsx /Data data.csv --header` | TSV: `--format tsv`; stdin: `--stdin` |
| Add table / validation / chart | officecli | `officecli add model.xlsx /Data --type table --prop ref=A1:D10` | Native structured workbook objects |
| Data transformation | pandas | `pd.read_excel(...)` -> transform -> write | pandas is PRIMARY for analysis |
| **Formula recalculation** | Python (L3) | `python3 scripts/recalc.py output.xlsx` | **officecli does not recalculate — MANDATORY after formula writes** |
| **Complex openpyxl formatting** | Python (L3/L4) | See `references/openpyxl_guide.md` | Styling beyond officecli |
| **Raw OOXML inspection/edit** | officecli (L2) | `officecli raw output.xlsx /xl/workbook.xml` | For L2 XML tweaks |
| Financial conventions | -- | Read `references/financial_conventions.md` | Blue input / black formula / source annotations |
| Edit existing workbook | -- | Read [editing.md](./editing.md) | Detailed editing guides |
| Create from scratch | -- | Read [creating.md](./creating.md) | Detailed creation recipes |

---

## 2. Reference-Based Editing (Edit > Create from Scratch)

When the user says "format like X.xlsx", "match existing style", "based on template", or provides a source file — **start from the source. Don't rebuild from scratch.**

### Core Rule: Preserve Existing Templates

When modifying files, **match existing format, style, and conventions exactly.** Excel workbooks often have:

- Named ranges that formulas depend on
- Conditional formatting rules on specific ranges
- Data validation on input cells
- Custom number formats per column
- Sheet protection / locked cells
- Hidden/very-hidden sheets

Rebuilding these from scratch silently breaks formulas, validation, and visual consistency.

### Workflow

1. **Copy the source**: `cp source.xlsx target.xlsx` — inherits sheets, named ranges, styles, validation, CF rules
2. **Open** with `officecli open target.xlsx` — daemon returns immediately (do NOT run as `run_in_background`)
3. **Clear data cells only** — keep sheet structure, named ranges, validation, conditional formatting
4. **Write new values** into the preserved structure — formulas auto-recalculate

### Template Sources (priority order)

1. **User-provided source file** — first-class template
2. **`tests/fixtures/*.xlsx`** — pre-built examples shipped with this skill
3. **`officecli-financial-model/` templates** — 3-statement, DCF, budget starting points
4. **`officecli-data-dashboard/` templates** — chart/pivot/CF starting points
5. **`officecli create`** blank — only when nothing else applies

### Example — Budget Template Reuse

```bash
# CORRECT: preserve named ranges + CF
cp Q3Budget.xlsx Q4Budget.xlsx
officecli open Q4Budget.xlsx
# Clear only data cells (keep headers, formulas, named ranges)
officecli set Q4Budget.xlsx "/Inputs/B2:B20" --prop value=""
# Write new Q4 inputs
officecli set Q4Budget.xlsx "/Inputs/B2" --prop value=15000 --prop type=number
officecli close Q4Budget.xlsx
python3 scripts/recalc.py Q4Budget.xlsx   # recalc formulas

# WRONG: rebuild from scratch, loses named ranges + CF
officecli create Q4Budget.xlsx
# ... all formulas break ...
```

---

## 3. Reference Materials & Script Map

officecli covers most XLSX tasks. pandas handles analysis. For formatting, recalc, and raw OOXML work, use these references + scripts.

### References (`references/`)

| File | Read when | Contains |
|------|-----------|----------|
| `references/cjk_handling.md` | Korean text width / auto-fit / column sizing | CJK auto-fit logic, `rFonts`, common width pitfalls |
| `references/financial_conventions.md` | **Financial model work** — 3-statement, DCF, budgets, assumption sheets | Blue=input, Black=formula, Green=link, numFmt conventions, source annotation rules |
| `references/openpyxl_guide.md` | Complex formatting beyond officecli — conditional formatting, data validation, charts, tables, named ranges | openpyxl API patterns, styling examples |

### Scripts (`scripts/`) — Python OOXML Toolkit

| Script | Run when | Command |
|--------|----------|---------|
| `scripts/xlsx_cli.py` | Unified Python CLI — unpack, save, validate, repair, recalc, text, sheet-overview, formula-audit, search | `python3 scripts/xlsx_cli.py {open\|save\|validate\|repair\|recalc\|text\|sheet-overview\|formula-audit\|search}` |
| `scripts/recalc.py` | **MANDATORY after formula writes** — openpyxl does not recalc, and Excel caches stale values | `python3 scripts/recalc.py output.xlsx` |
| `scripts/run_tests.py` | Run skill regression tests | `python3 scripts/run_tests.py` |

### Editing Escalation Ladder

When officecli can't do the job, escalate in this order:

| Level | When | Tool |
|-------|------|------|
| **L1** officecli high-level | Typical cell/sheet/chart add/set/remove | `officecli add/set/remove/query/view/batch/import` |
| **L2** officecli `raw` / `raw-set` | Raw OOXML inspection/edit — workbook.xml, sharedStrings.xml, sheet XML | `officecli raw FILE /xl/PATH.xml` or `raw-set` |
| **L3** Python script | Formula recalc (MANDATORY), validate, formula-audit, bulk OOXML ops | `python3 scripts/xlsx_cli.py ...` or `scripts/recalc.py` |
| **L4** pandas + openpyxl | Complex styling, data pipelines, multi-source joins | `pd.read_excel` → transform → `openpyxl` → save |

**Escalation signals:**
- **Wrote formulas via officecli** → **L3** `scripts/recalc.py` (non-negotiable)
- Need **data transforms** (groupby, pivot, merge) → **L4** pandas
- Need **complex CF / data validation / named-range math** → **L4** openpyxl (see `references/openpyxl_guide.md`)
- Need **financial convention** (blue input, black formula, source annotation) → Read `references/financial_conventions.md`
- Need **raw OOXML tweak** (shared strings, theme XML) → **L2** `officecli raw-set`

---

## 4. Subskill References

Read **only** the subskill relevant to the current task. Do not preload all.

| Subskill | Path (relative) | When to read |
|----------|-----------------|--------------|
| **officecli-financial-model** | `./officecli-financial-model/SKILL.md` | 3-statement models, DCF, LBO, revenue builds, assumption sheets |
| **officecli-data-dashboard** | `./officecli-data-dashboard/SKILL.md` | Charts, pivot tables, conditional formatting, dashboard layouts |
| **creating.md** | `./creating.md` | Detailed recipes for building workbooks from scratch |
| **editing.md** | `./editing.md` | Modification guides for existing workbooks |

---

## 5. Design Principles for Spreadsheets

**Professional spreadsheets need clear structure, correct formulas, and intentional formatting.**

### Core Rule: Preserve Existing Templates (MANDATORY)

When modifying files, match existing format, style, and conventions exactly. Rebuilding from scratch silently breaks named ranges, CF rules, and validation. See §2.

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

> Full financial convention details: read `references/financial_conventions.md`.

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

## 6. Mandatory Verification (NEVER SKIP)

After ANY XLSX edit, ALWAYS execute both steps:

```bash
# Step 1: structural validation
officecli validate output.xlsx

# Step 2: visual PDF proof
soffice --headless --convert-to pdf --outdir /tmp output.xlsx
# Check: formula results, cell formatting, chart rendering, merged cells
```

If formulas were written, ADD:

```bash
# Step 3: recalc pass (formulas do NOT calculate until this runs)
python3 scripts/recalc.py output.xlsx
```

Skip none. `validate` catches structural errors; the PDF catches rendering issues (truncated CJK, broken charts, invisible text); `recalc.py` updates cached values for all formulas.

---

## 7. Prerequisite Check

```bash
which officecli || echo "MISSING: install officecli first — see https://officecli.ai"
which soffice || echo "OPTIONAL: install LibreOffice for PDF verification"
python3 -c "import pandas, openpyxl" || echo "MISSING: pip install pandas openpyxl"
```

## 8. Tool Discovery

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

## 9. Core Workflows

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

> **Error decoding:** `'X' is an invalid start of a value` = shell syntax leaked into JSON. Use heredoc `cat <<'EOF' | officecli batch FILE` with single-quoted delimiter.

### Resident Mode

```bash
officecli open data.xlsx        # Returns IMMEDIATELY; daemon in bg
officecli add data.xlsx ...     # All commands run in memory -- fast
officecli set data.xlsx ...
officecli close data.xlsx       # Write once to disk
```

> **Do NOT run `officecli open` as a background shell job.** It returns immediately and the daemon lives in the background automatically. Running it as a monitored shell creates zombies and file locks.

### CSV / TSV Import

```bash
officecli import f.xlsx /Sheet1 data.csv --header           # CSV
officecli import f.xlsx /Sheet1 data.tsv --header --format tsv  # TSV
cat data.csv | officecli import f.xlsx /Sheet1 --stdin --header  # stdin
```

### Chart Creation

```bash
# Add a column chart from data range
officecli add doc.xlsx /Sheet1 --type chart --prop chartType=column --prop data=Sheet1!A1:D10 --prop title="Revenue by Quarter"

# For detailed chart customization (series, axes, legends), read ./officecli-data-dashboard/SKILL.md
```

---

## 10. pandas Pipeline

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
python3 scripts/recalc.py output.xlsx   # if formulas added
```

This path keeps pandas focused on transforms and lets officecli own the OOXML package. One `import` command replaces dozens of `set cell` calls.

For complex openpyxl-based styling (CF gradients, data bars, custom chart XML), see `references/openpyxl_guide.md`.

---

## 11. Formula Recalculation (CRITICAL)

**officecli writes formulas but does NOT recalculate them.** openpyxl does not recalc either. Excel displays the cached value until recalc runs.

Always run a recalc pass after formula generation:

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

## 12. Number Format Reference

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

## 13. Common Pitfalls

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
| **Rebuilding existing template** | `cp source.xlsx target.xlsx` first. Named ranges, CF, validation cannot be trivially recreated. See §2 |
| **`officecli open` as background shell** | Run foreground — returns immediately, daemon runs in bg automatically |
| **Batch JSON `'X' is an invalid start of a value`** | Shell syntax leaked. Use heredoc: `cat <<'EOF' \| officecli batch FILE.xlsx` |
| **Forgot `scripts/recalc.py` after formula writes** | officecli does NOT recalc. Cached values stay stale. Always run recalc.py before delivery |

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
- [ ] **`python3 scripts/recalc.py` executed after formula writes**
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
- [ ] Comments on hardcoded assumption values documenting their source (see `references/financial_conventions.md`)

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
3. `python3 scripts/recalc.py` if formulas present
4. Run formula error queries (all 5 error types)
5. List issues found (if none found, look again more critically)
6. Fix issues
7. Re-verify affected areas -- one fix often creates another problem
8. Repeat until a full pass reveals no new issues

**Do not declare success until you have completed at least one fix-and-verify cycle.**

---

## 14. Anti-Patterns (NEVER DO)

**Formula results hardcoded as values -- STRICTLY FORBIDDEN.** The workbook must remain recalculable when inputs change.

**Fictional example data leaking into output -- FORBIDDEN.** Never use placeholder names in deliverable workbooks.

**Merged cell abuse -- FORBIDDEN.** Merged cells break sorting, filtering, screen readers, and programmatic access. Use center-across-selection or column width adjustments instead. Exception: a single title row.

**Sheet names containing `!` -- ESCAPE WARNING.** Excel uses `!` as the sheet-range delimiter.

**Rebuilding existing template from scratch -- STRICTLY FORBIDDEN** when user provides a source file. `cp` first; match existing conventions. Named ranges, CF, validation, locked cells cannot be trivially recreated. See §2.

**Skipping `recalc.py` after formula writes -- FORBIDDEN.** Cached formula values stay stale until recalc runs. Deliverables show wrong numbers.

**Ignoring reference materials -- FORBIDDEN.** For financial conventions, read `references/financial_conventions.md`. For complex openpyxl styling, read `references/openpyxl_guide.md`. The Pre-officecli openpyxl/pandas workflow is still available.

---

## 15. Known Issues

| Issue | Workaround |
|---|---|
| Chart series cannot be added after creation | Delete and recreate with all series |
| No visual preview | Use `view text`/`annotated`/`stats`/`issues` for verification |
| Formula cached values for new formulas | Run `scripts/recalc.py` — cached value updates when opened in Excel/LibreOffice afterwards |
| Batch intermittent failure | Keep batches to 8-12 ops; retry failures individually |
| Data bar default min/max invalid | Always specify explicit `--prop min=N --prop max=N` |
| Cell protection requires sheet protection | `locked` only takes effect when sheet is protected |

---

## 16. Dependencies

| Tool | Why it exists | Status |
|------|---------------|--------|
| `officecli` (PATH) | Primary Excel CLI | Required |
| `pandas` | DataFrame analysis pipeline | Primary for transforms |
| `openpyxl` | pandas Excel engine + fallback editing (L4) | Required for L3/L4 |
| `python3` | Helper scripts (`scripts/*.py`) | Required for L3 |
| `soffice` | Recalculation / PDF export | Optional fallback |
