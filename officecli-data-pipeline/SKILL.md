---
name: officecli-data-pipeline
description: "Pandas DataFrame → Excel pipeline. Export pandas split JSON, write explicit cells with officecli batch --input, close, read back persisted values, then format and validate. Supports CJK, embedded newlines, number formatting, conditional formatting, and charts."
metadata:
  openclaw:
    emoji: "📊"
    requires: "officecli (>= 1.0.28), python3, pandas"
---

# officecli-data-pipeline

Overlay skill for OfficeCLI that bridges Python pandas DataFrames with formatted Excel documents.

> **Architecture**: pandas creates the data → split JSON preserves values and embedded newlines → officecli writes explicit cells with `batch --input` → officecli closes, reads back, formats, and validates.
> This path keeps pandas focused on transforms and lets officecli own the OOXML package from creation through validation.
>
> **Install consent contract**: probe with the agent's actual shell — `command -v officecli` on
> POSIX, `Get-Command officecli -ErrorAction SilentlyContinue` in PowerShell, or portably
> `officecli --version`. `command -v` is NOT a PowerShell builtin: on Windows it prints nothing,
> sets no exit code, and raises no error, so a working install reads as missing and the agent asks
> to install what is already there (#298). If genuinely missing, do not auto-install.
> Ask the user to install the supported fork from `https://github.com/lidge-jun/OfficeCLI`, continue
> with a lightweight pandas/openpyxl fallback after stating formatting/validation limits, or stop.
> If the user chooses lightweight mode, save that preference to memory for future Office work.

### Windows safety contract

- On Windows, **never use `officecli import` for bulk writes**. Released builds can report success while persisting an empty-cell skeleton.
- Generate explicit cell commands with `scripts/dataframe_to_batch.py`, save them to a UTF-8 JSON file, and run `officecli batch WORKBOOK --input COMMANDS.json`.
- Prefer `--input` over inline `--commands`; it avoids Windows shell quoting and command-length hazards.
- After the last mutation, run `officecli close WORKBOOK`, then verify exact persisted values with `scripts/verify_persisted_cells.py`.
- `officecli validate`, row counts, and successful exit codes are not proof that values were saved. Read back representative headers, CJK text, embedded-newline cells, and numeric cells from the closed workbook.
- `officecli import` is legacy opt-in on non-Windows only, after that exact OfficeCLI build has been independently verified. Persisted read-back remains mandatory.

Commands below use `python`, which is the normal Windows launcher. On hosts that
only expose `python3`, substitute that command without changing the arguments.

---

## When to Use

- Converting pandas DataFrame to a formatted Excel report
- Creating data reports from CSV, JSON, or database sources
- Building multi-sheet dashboards with Python data + officecli formatting
- Batch data processing pipelines that need styled output
- Any workflow where raw data needs professional formatting before delivery

---

## Pipeline Architecture

```
┌─────────────┐    ┌───────────────┐    ┌──────────────┐    ┌────────────────┐
│   pandas     │ →  │  split JSON   │ →  │  officecli   │ →  │ close/read-back│
│  DataFrame   │    │ values + rows │    │ batch --input│    │ format/validate│
└─────────────┘    └───────────────┘    └──────────────┘    └────────────────┘
  Data transforms     UTF-8 + newlines    Explicit cells       Persisted proof
  Joins, aggregates   Type-safe values    Native workbook      Schema + layout
```

**Why export split JSON instead of writing `.xlsx` directly?** officecli formatting is:
1. Declarative (one command per style) vs imperative (multiple Python API calls)
2. Scriptable in shell (composable with other CLI tools)
3. Batchable (single open/save cycle for all formatting)
4. Owned end-to-end by officecli, while exact persisted read-back catches silent empty-workbook failures

---

## Quick Pipeline: Single Sheet

### Step 1: Export Data with Python

```python
import pandas as pd

df = pd.DataFrame({
    "제품명": ["김치냉장고", "에어컨", "세탁기", "건조기"],
    "매출액": [15000000, 23000000, 18000000, 12000000],
    "전년비": [1.25, 1.15, 0.95, 1.30],
    "카테고리": ["가전", "가전", "가전", "가전"],
})

df.to_json(
    "sales_report.split.json",
    orient="split",
    force_ascii=False,
    date_format="iso",
)
print(f"Prepared {len(df)} rows for explicit-cell writing")
```

### Step 2: Format with officecli

```bash
# Create workbook and write every non-null value to an explicit cell.
officecli create sales_report.xlsx
python scripts/dataframe_to_batch.py \
  --sheet-json Sheet1=sales_report.split.json \
  --output sales_report.data.json
officecli batch sales_report.xlsx --input sales_report.data.json

# Header row styling
officecli set sales_report.xlsx '/Sheet1/A1:D1' \
  --prop font.bold=true --prop font.name="Malgun Gothic" --prop font.size=12

# Number formatting
officecli set sales_report.xlsx '/Sheet1/B2:B5' --prop numFmt="#,##0"
officecli set sales_report.xlsx '/Sheet1/C2:C5' --prop numFmt="0.0%"

# Column widths (accommodate Korean text)
officecli set sales_report.xlsx '/Sheet1/col[A]' --prop width=18
officecli set sales_report.xlsx '/Sheet1/col[B]' --prop width=15
officecli set sales_report.xlsx '/Sheet1/col[C]' --prop width=12
officecli set sales_report.xlsx '/Sheet1/col[D]' --prop width=12

# Freeze header row
officecli set sales_report.xlsx /Sheet1 --prop freeze=A2

```

### Step 3: Batch Formatting (Recommended)

Save the following UTF-8 JSON as `sales_report.format.json`. File input performs
all operations in one open/save cycle without Windows shell-quoting hazards:

```json
[
  {"command":"set","path":"/Sheet1/A1:D1","props":{"font.bold":"true","font.size":"12","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/Sheet1/B2:B5","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/Sheet1/C2:C5","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/Sheet1/col[A]","props":{"width":"18"}},
  {"command":"set","path":"/Sheet1/col[B]","props":{"width":"15"}},
  {"command":"set","path":"/Sheet1/col[C]","props":{"width":"12"}},
  {"command":"set","path":"/Sheet1/col[D]","props":{"width":"12"}},
  {"command":"set","path":"/Sheet1","props":{"freeze":"A2"}}
]
```

```bash
officecli batch sales_report.xlsx --input sales_report.format.json
officecli close sales_report.xlsx
```

Save representative exact values as `sales_report.expect.json`:

```json
{
  "/Sheet1/A1": "제품명",
  "/Sheet1/A2": "김치냉장고",
  "/Sheet1/B2": "15000000"
}
```

```bash
python scripts/verify_persisted_cells.py sales_report.xlsx \
  --expect-json sales_report.expect.json
officecli validate sales_report.xlsx
```

---

## Conditional Formatting

### Data Bars

```bash
# Add data bars to revenue column
officecli add sales_report.xlsx '/매출데이터' --type databar \
  --prop range=B2:B5 --prop color=4472C4
```

### Color Scale (Heatmap)

```bash
# Green-to-red heatmap on growth rates
officecli add sales_report.xlsx '/매출데이터' --type colorscale \
  --prop range=C2:C5
```

### Icon Sets

```bash
# Traffic light icons for performance indicators
officecli add sales_report.xlsx '/매출데이터' --type iconset \
  --prop range=C2:C5
```

### Formula-Based Conditional Formatting

```bash
# Highlight cells where growth rate < 100% (declining)
officecli add sales_report.xlsx '/매출데이터' --type formulacf \
  --prop range=C2:C5 --prop formula='$C2<1' --prop fill=FF6B6B

# Highlight top performers (> 120%)
officecli add sales_report.xlsx '/매출데이터' --type formulacf \
  --prop range=C2:C5 --prop formula='$C2>=1.2' --prop fill=51CF66
```

---

## Charts

### Add Chart from Data Range

```bash
# Column chart from existing data
officecli add sales_report.xlsx '/매출데이터' --type chart \
  --prop chartType=bar \
  --prop dataRange="매출데이터!A1:B5" \
  --prop title="제품별 매출액" \
  --prop width=10 --prop height=15 \
  --prop x=6 --prop y=1

# Line chart for trends
officecli add sales_report.xlsx '/매출데이터' --type chart \
  --prop chartType=line \
  --prop dataRange="매출데이터!A1:C5" \
  --prop title="매출 및 성장률" \
  --prop legend=bottom
```

### Chart with Inline Data

```bash
officecli add sales_report.xlsx '/매출데이터' --type chart \
  --prop chartType=pie \
  --prop categories="김치냉장고,에어컨,세탁기,건조기" \
  --prop data="Sales:15000000,23000000,18000000,12000000" \
  --prop title="매출 비중" \
  --prop dataLabels=true \
  --prop labelPos=outside
```

---

## Multi-Sheet Reports

### Step 1: Export Multiple DataFrames

```python
import pandas as pd

df_sales = pd.DataFrame({
    "월": ["1월", "2월", "3월"],
    "매출액": [50000000, 55000000, 48000000],
    "영업이익": [8000000, 9500000, 7200000],
})

df_costs = pd.DataFrame({
    "비목": ["인건비", "재료비", "마케팅", "기타"],
    "금액": [25000000, 15000000, 8000000, 5000000],
    "비율": [0.47, 0.28, 0.15, 0.10],
})

df_summary = pd.DataFrame({
    "지표": ["총매출", "총비용", "순이익", "이익률"],
    "금액": [153000000, 53000000, 100000000, 0.654],
})

df_sales.to_json("sales.split.json", orient="split", force_ascii=False)
df_costs.to_json("costs.split.json", orient="split", force_ascii=False)
df_summary.to_json("summary.split.json", orient="split", force_ascii=False)
```

### Step 2: Format All Sheets with Batch

```bash
officecli create quarterly_report.xlsx
officecli add quarterly_report.xlsx / --type sheet --prop name="매출"
officecli add quarterly_report.xlsx / --type sheet --prop name="비용"
officecli add quarterly_report.xlsx / --type sheet --prop name="요약"
python scripts/dataframe_to_batch.py \
  --sheet-json 매출=sales.split.json \
  --sheet-json 비용=costs.split.json \
  --sheet-json 요약=summary.split.json \
  --output quarterly.data.json
officecli batch quarterly_report.xlsx --input quarterly.data.json
```

Save the following as `quarterly.format.json`:

```json
[
  {"command":"set","path":"/매출/A1:C1","props":{"font.bold":"true","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/매출/B2:C4","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/매출/col[A]","props":{"width":"10"}},
  {"command":"set","path":"/매출/col[B]","props":{"width":"15"}},
  {"command":"set","path":"/매출/col[C]","props":{"width":"15"}},
  {"command":"set","path":"/매출","props":{"freeze":"A2"}},

  {"command":"set","path":"/비용/A1:C1","props":{"font.bold":"true","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/비용/B2:B5","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/비용/C2:C5","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/비용/col[A]","props":{"width":"12"}},
  {"command":"set","path":"/비용/col[B]","props":{"width":"15"}},

  {"command":"set","path":"/요약/A1:B1","props":{"font.bold":"true","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/요약/B2:B3","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/요약/B4","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/요약/B5","props":{"numFmt":"0.0%"}}
]
```

```bash
officecli batch quarterly_report.xlsx --input quarterly.format.json
officecli close quarterly_report.xlsx
python scripts/verify_persisted_cells.py quarterly_report.xlsx \
  --expect-json quarterly.expect.json
officecli validate quarterly_report.xlsx
```

---

## Legacy CSV Import (Opt-in Only)

Do not use this path on Windows. Convert CSV/TSV with pandas, export split JSON,
then use the explicit-cell batch path above. The commands below are allowed only
on a non-Windows host after verifying the exact OfficeCLI build, and still require
close plus exact persisted read-back:

```bash
# Create workbook and import CSV directly
officecli create report.xlsx
officecli import report.xlsx /Sheet1 data.csv --header

# Format the imported data
officecli set report.xlsx '/Sheet1/A1:D1' \
  --prop font.bold=true --prop font.name="Malgun Gothic"

# Add autofilter for data exploration
officecli add report.xlsx /Sheet1 --type autofilter --prop range=A1:D1

officecli close report.xlsx
python scripts/verify_persisted_cells.py report.xlsx --expect-json report.expect.json
officecli validate report.xlsx
```

### TSV Import

Legacy non-Windows verified builds only:

```bash
officecli import report.xlsx /Sheet1 data.tsv --format tsv --header
```

### Stdin Import (Pipe from Other Tools)

Legacy non-Windows verified builds only:

```bash
# Pipe query results directly into Excel
cat query_results.csv | officecli import report.xlsx /Sheet1 --stdin --header
```

---

## Number Format Reference

Common format codes for `--prop numFmt=`:

| Format Code | Example Output | Use Case |
|------------|----------------|----------|
| `#,##0` | 15,000,000 | Integer with comma separators |
| `#,##0.00` | 15,000,000.00 | Currency (2 decimals) |
| `0.0%` | 125.0% | Percentage (1 decimal) |
| `0%` | 125% | Percentage (no decimal) |
| `0.00` | 1.25 | Decimal (2 places) |
| `yyyy-mm-dd` | 2026-03-27 | ISO date |
| `yyyy"년" mm"월" dd"일"` | 2026년 03월 27일 | Korean date |
| `$#,##0` | $15,000,000 | USD currency |
| `₩#,##0` | ₩15,000,000 | KRW currency |
| `¥#,##0` | ¥15,000,000 | JPY/CNY currency |

```bash
# Apply Korean currency format
officecli set data.xlsx '/Sheet1/B2:B100' --prop numFmt="₩#,##0"

# Apply Korean date format
officecli set data.xlsx '/Sheet1/A2:A100' --prop numFmt='yyyy"년" mm"월" dd"일"'
```

---

## End-to-End Sequence

Complete pipeline from data generation to persisted-value proof:

```python
import pandas as pd

df = pd.DataFrame([
    {"제품명": "김치냉장고", "설명": "첫 줄\n둘째 줄", "매출액": 15000000},
    {"제품명": "에어컨", "설명": "여름 상품", "매출액": 23000000},
])
df.to_json("monthly_sales.split.json", orient="split", force_ascii=False)
```

```bash
officecli create monthly_sales.xlsx
officecli add monthly_sales.xlsx / --type sheet --prop name="월별매출"
python scripts/dataframe_to_batch.py \
  --sheet-json 월별매출=monthly_sales.split.json \
  --output monthly_sales.data.json
officecli batch monthly_sales.xlsx --input monthly_sales.data.json

# Save formatting commands as monthly_sales.format.json, then apply them.
officecli batch monthly_sales.xlsx --input monthly_sales.format.json
officecli close monthly_sales.xlsx

# Include a header, CJK, embedded newline, and number in this expectations file.
python scripts/verify_persisted_cells.py monthly_sales.xlsx \
  --expect-json monthly_sales.expect.json
officecli validate monthly_sales.xlsx
```

Example `monthly_sales.expect.json`:

```json
{
  "/월별매출/A1": "제품명",
  "/월별매출/A2": "김치냉장고",
  "/월별매출/B2": "첫 줄\n둘째 줄",
  "/월별매출/C2": "15000000"
}
```

---

## Validation Checklist

After every pipeline run, verify:

```bash
# 1. Flush and release the workbook before proving persistence
officecli close output.xlsx

# 2. Exact persisted values: header, CJK, newline, and number
python scripts/verify_persisted_cells.py output.xlsx --expect-json output.expect.json

# 3. Schema validation (necessary, but not sufficient on its own)
officecli validate output.xlsx

# 4. Number formats applied correctly
officecli get output.xlsx '/Sheet1/B2' --json
# Check numFmt in response

# 5. Conditional formatting present
officecli get output.xlsx '/Sheet1' --json
# Check for cf (conditional formatting) entries
```

**Pass criteria:**
- [ ] Workbook was closed before verification
- [ ] Exact representative values were read from the persisted workbook
- [ ] CJK and embedded-newline values match byte-for-byte
- [ ] `officecli validate` passes with no errors
- [ ] Row count matches DataFrame length + 1 (header)
- [ ] Number formats show commas/percentages as expected
- [ ] Conditional formatting highlights correct cells
- [ ] Charts reference correct data ranges

---

## Quick Reference Card

| Task | Command |
|------|---------|
| DataFrame → batch JSON | `python scripts/dataframe_to_batch.py --sheet-json Sheet1=data.split.json --output data.batch.json` |
| Safe bulk write | `officecli batch data.xlsx --input data.batch.json` |
| Legacy import | Non-Windows verified builds only: `officecli import data.xlsx /Sheet1 data.csv --header` |
| Header styling | `officecli set f.xlsx '/Sheet1/A1:D1' --prop font.bold=true --prop font.name="Malgun Gothic"` |
| Number format | `officecli set f.xlsx '/Sheet1/B2:B99' --prop numFmt="#,##0"` |
| Percentage | `officecli set f.xlsx '/Sheet1/C2:C99' --prop numFmt="0.0%"` |
| Column width | `officecli set f.xlsx '/Sheet1/col[A]' --prop width=18` |
| Freeze pane | `officecli set f.xlsx /Sheet1 --prop freeze=A2` |
| Data bar | `officecli add f.xlsx /Sheet1 --type databar --prop range=B2:B99` |
| Highlight rule | `officecli add f.xlsx /Sheet1 --type formulacf --prop range=... --prop formula=...` |
| Chart | `officecli add f.xlsx /Sheet1 --type chart --prop chartType=bar --prop dataRange=...` |
| Autofilter | `officecli add f.xlsx /Sheet1 --type autofilter --prop range=A1:D1` |
| Batch format | `officecli batch f.xlsx --input format.commands.json` |
| Flush and release | `officecli close f.xlsx` |
| Persisted read-back | `python scripts/verify_persisted_cells.py f.xlsx --expect-json expected.json` |
| Validate | `officecli validate f.xlsx` |
