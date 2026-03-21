# CJK / Korean Text Handling

## Column Width for CJK

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

## Korean Fonts

```python
from openpyxl.styles import Font

# Cross-platform safe
ko_font = Font(name="Noto Sans KR", size=11)

# Windows-only environments
ko_font = Font(name="Malgun Gothic", size=11)

# Header
ko_header = Font(name="Noto Sans KR", size=12, bold=True)
```

`charset=134` is not needed — modern xlsx uses UTF-8 internally. Setting charset can cause encoding confusion in some viewers.

| Font               | License   | Cross-platform | Best for           |
| ------------------ | --------- | -------------- | ------------------ |
| Noto Sans KR       | OFL       | Win/Mac/Linux  | Safest choice      |
| Pretendard         | OFL       | Win/Mac/Linux  | Modern UI          |
| Malgun Gothic      | MS bundle | Windows only   | Windows-only files |
| NanumGothic        | OFL       | Win/Mac/Linux  | General Korean     |

## PivotTable Alternative

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

ratio = check_contrast("FFFFFF", "4472C4")
assert ratio >= 4.5, f"Contrast insufficient: {ratio:.1f}:1 (need >= 4.5:1)"
```
