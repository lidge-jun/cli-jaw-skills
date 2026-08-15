# openpyxl Reference Guide

> [openpyxl ReadTheDocs](https://openpyxl.readthedocs.io/en/stable/) — MIT License

```bash
pip install openpyxl
```

## Basic Structure

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

> Opening with `data_only=True` replaces formulas with cached values — saving permanently loses formulas.

## Styling

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

## Tables

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

## Performance Tips for Large Files

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

## Conditional Formatting

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

## Data Validation (Dropdowns)

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

## Charts

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

### Chart Style Guide

| Chart Type           | When to Use        | openpyxl style |
| -------------------- | ------------------ | -------------- |
| Column bar (`col`)   | Category comparison| `style=10`     |
| Horizontal bar (`bar`)| Long labels       | `style=11`     |
| Line (`line`)        | Time series trends | `style=13`     |
| Pie                  | Ratios/share       | `style=26`     |
| Area (`area`)        | Cumulative trends  | `style=10`     |

## Named Ranges

```python
from openpyxl.workbook.defined_name import DefinedName

ref = DefinedName('revenue_growth', attr_text="Inputs!$B$1")
wb.defined_names.add(ref)

# Use in formulas for readability
ws['B2'] = '=revenue_2024 * (1 + revenue_growth)'
# vs unreadable: '=Inputs!$B$5 * (1 + Inputs!$B$1)'
```
