# Financial Model Conventions

## Color Coding (Industry Standard)

| Color  | RGB         | Purpose                              |
| ------ | ----------- | ------------------------------------ |
| Blue   | `0,0,255`   | Hard-coded inputs, scenario toggles  |
| Black  | `0,0,0`     | Formulas and calculated results      |
| Green  | `0,128,0`   | Values pulled from other sheets      |
| Red    | `255,0,0`   | External file references             |
| Yellow | `255,255,0` | Key assumptions needing attention    |

## Number Formatting Standards

| Data Type     | Format               | Example                    |
| ------------- | -------------------- | -------------------------- |
| Years         | Text string          | `"2024"` not `2,024`       |
| Currency      | `$#,##0`             | Always specify units in headers: `"Revenue ($mm)"` |
| Zeros         | Show as dash         | `$#,##0;($#,##0);"-"`     |
| Percentages   | `0.0%`               | One decimal default        |
| Multiples     | `0.0x`               | For EV/EBITDA, P/E         |
| Negatives     | Parentheses          | `(123)` not `-123`         |

## Korean Financial Formats

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

## 3-Sheet Separation Principle

```
Workbook
├── Inputs        ← Blue text, user-adjustable assumptions
├── Calculations  ← Black text, formulas only (no hard-coding)
└── Outputs       ← Summary dashboard, charts
```

## Document Hard-coded Sources

Record the source next to input values:
```python
ws['A1'] = 'Revenue Growth Rate'
ws['B1'] = 0.15
ws['C1'] = 'Source: Company 10-K, FY2024, p.45'
```
