---
name: officecli-data-pipeline
description: "Pandas DataFrame → Excel pipeline. Export CSV/TSV from pandas, import with officecli, then format and validate. Supports CJK headers, number formatting, conditional formatting, and charts."
metadata:
  openclaw:
    emoji: "📊"
    requires: "officecli (>= 1.0.28), python3, pandas"
---

# officecli-data-pipeline

Overlay skill for OfficeCLI that bridges Python pandas DataFrames with formatted Excel documents.

> **Architecture**: pandas creates the data → CSV/TSV export preserves the table cleanly → officecli creates/imports the workbook → officecli formats and validates.
> This path keeps pandas focused on transforms and lets officecli own the OOXML package from creation through validation.

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
┌─────────────┐    ┌───────────────┐    ┌──────────────┐    ┌──────────────┐
│   pandas     │ →  │   CSV / TSV    │ →  │  officecli   │ →  │  officecli   │
│  DataFrame   │    │ export table   │    │ create/import│    │ format/valid │
└─────────────┘    └───────────────┘    └──────────────┘    └──────────────┘
  Data transforms     Portable rows      Native workbook      Schema + layout
  Joins, aggregates   Header-safe text   ownership            verification
```

**Why export CSV/TSV first instead of writing `.xlsx` directly?** officecli formatting is:
1. Declarative (one command per style) vs imperative (multiple Python API calls)
2. Scriptable in shell (composable with other CLI tools)
3. Batchable (single open/save cycle for all formatting)
4. Owned end-to-end by officecli, so `officecli validate` stays aligned with the generated workbook

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

df.to_csv("sales_report.csv", index=False)
print(f"Written {len(df)} rows to sales_report.csv")
```

### Step 2: Format with officecli

```bash
# Create workbook and import pandas output
officecli create sales_report.xlsx
officecli import sales_report.xlsx /Sheet1 sales_report.csv --header

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

# Validate
officecli validate sales_report.xlsx
```

### Step 3: Batch Formatting (Recommended)

Batch mode performs all operations in a single open/save cycle — much faster:

```bash
officecli batch sales_report.xlsx --commands '[
  {"command":"set","path":"/Sheet1/A1:D1","props":{"font.bold":"true","font.size":"12","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/Sheet1/B2:B5","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/Sheet1/C2:C5","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/Sheet1/col[A]","props":{"width":"18"}},
  {"command":"set","path":"/Sheet1/col[B]","props":{"width":"15"}},
  {"command":"set","path":"/Sheet1/col[C]","props":{"width":"12"}},
  {"command":"set","path":"/Sheet1/col[D]","props":{"width":"12"}},
  {"command":"set","path":"/Sheet1","props":{"freeze":"A2"}}
]'
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

df_sales.to_csv("sales.csv", index=False)
df_costs.to_csv("costs.csv", index=False)
df_summary.to_csv("summary.csv", index=False)
```

### Step 2: Format All Sheets with Batch

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
]'

officecli validate quarterly_report.xlsx
```

---

## CSV Import Pipeline

For simple CSV-to-Excel conversion without Python:

```bash
# Create workbook and import CSV directly
officecli create report.xlsx
officecli import report.xlsx /Sheet1 data.csv --header

# Format the imported data
officecli set report.xlsx '/Sheet1/A1:D1' \
  --prop font.bold=true --prop font.name="Malgun Gothic"

# Add autofilter for data exploration
officecli add report.xlsx /Sheet1 --type autofilter --prop range=A1:D1

officecli validate report.xlsx
```

### TSV Import

```bash
officecli import report.xlsx /Sheet1 data.tsv --format tsv --header
```

### Stdin Import (Pipe from Other Tools)

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

## End-to-End Example Script

Complete pipeline from data generation to validated output:

```bash
#!/bin/bash
set -euo pipefail

OUTPUT="monthly_sales_$(date +%Y%m).xlsx"

# Step 1: Generate data with Python
python3 -c "
import pandas as pd
import random

months = ['1월','2월','3월','4월','5월','6월']
products = ['김치냉장고','에어컨','세탁기','건조기','식기세척기']

rows = []
for product in products:
    for month in months:
        revenue = random.randint(8000000, 30000000)
        growth = round(random.uniform(0.85, 1.35), 2)
        rows.append({'제품명': product, '월': month, '매출액': revenue, '성장률': growth})

df = pd.DataFrame(rows)
df.to_csv('monthly_sales.csv', index=False)
print(f'Generated {len(df)} rows')
"

# Step 2: Create workbook and import CSV
officecli create "$OUTPUT"
officecli add "$OUTPUT" / --type sheet --prop name="월별매출"
officecli import "$OUTPUT" /월별매출 monthly_sales.csv --header

# Step 3: Format with officecli batch
officecli batch "$OUTPUT" --commands '[
  {"command":"set","path":"/월별매출/A1:D1","props":{"font.bold":"true","font.size":"11","font.name":"Malgun Gothic"}},
  {"command":"set","path":"/월별매출/C2:C31","props":{"numFmt":"#,##0"}},
  {"command":"set","path":"/월별매출/D2:D31","props":{"numFmt":"0.0%"}},
  {"command":"set","path":"/월별매출/col[A]","props":{"width":"16"}},
  {"command":"set","path":"/월별매출/col[B]","props":{"width":"8"}},
  {"command":"set","path":"/월별매출/col[C]","props":{"width":"15"}},
  {"command":"set","path":"/월별매출/col[D]","props":{"width":"10"}},
  {"command":"set","path":"/월별매출","props":{"freeze":"A2"}},
  {"command":"add","path":"/월별매출","type":"autofilter","props":{"range":"A1:D1"}},
  {"command":"add","path":"/월별매출","type":"databar","props":{"range":"C2:C31","color":"4472C4"}},
  {"command":"add","path":"/월별매출","type":"formulacf","props":{"range":"D2:D31","formula":"$D2<1","fill":"FF6B6B"}},
  {"command":"add","path":"/월별매출","type":"formulacf","props":{"range":"D2:D31","formula":"$D2>=1.2","fill":"51CF66"}}
]'

# Step 4: Add chart
officecli add "$OUTPUT" '/월별매출' --type chart \
  --prop chartType=bar \
  --prop dataRange="월별매출!A1:C31" \
  --prop title="월별 제품 매출" \
  --prop width=12 --prop height=18 \
  --prop x=6 --prop y=1

# Step 5: Validate
officecli validate "$OUTPUT"
echo "Pipeline complete: $OUTPUT"
```

---

## Validation Checklist

After every pipeline run, verify:

```bash
# 1. Schema validation
officecli validate output.xlsx

# 2. Row/column count matches expectation
officecli view output.xlsx text --end 3
# Verify header + first few data rows look correct

# 3. CJK text renders correctly
officecli view output.xlsx text | head -5
# Korean/Japanese/Chinese characters should be readable

# 4. Number formats applied correctly
officecli get output.xlsx '/Sheet1/B2' --json
# Check numFmt in response

# 5. Conditional formatting present
officecli get output.xlsx '/Sheet1' --json
# Check for cf (conditional formatting) entries
```

**Pass criteria:**
- [ ] `officecli validate` passes with no errors
- [ ] Row count matches DataFrame length + 1 (header)
- [ ] CJK text displays correctly in `view text`
- [ ] Number formats show commas/percentages as expected
- [ ] Conditional formatting highlights correct cells
- [ ] Charts reference correct data ranges

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Import CSV | `officecli import data.xlsx /Sheet1 data.csv --header` |
| Header styling | `officecli set f.xlsx '/Sheet1/A1:D1' --prop font.bold=true --prop font.name="Malgun Gothic"` |
| Number format | `officecli set f.xlsx '/Sheet1/B2:B99' --prop numFmt="#,##0"` |
| Percentage | `officecli set f.xlsx '/Sheet1/C2:C99' --prop numFmt="0.0%"` |
| Column width | `officecli set f.xlsx '/Sheet1/col[A]' --prop width=18` |
| Freeze pane | `officecli set f.xlsx /Sheet1 --prop freeze=A2` |
| Data bar | `officecli add f.xlsx /Sheet1 --type databar --prop range=B2:B99` |
| Highlight rule | `officecli add f.xlsx /Sheet1 --type formulacf --prop range=... --prop formula=...` |
| Chart | `officecli add f.xlsx /Sheet1 --type chart --prop chartType=bar --prop dataRange=...` |
| Autofilter | `officecli add f.xlsx /Sheet1 --type autofilter --prop range=A1:D1` |
| Batch format | `officecli batch f.xlsx --commands '[...]'` |
| Validate | `officecli validate f.xlsx` |
