# Workbook Design System Reference

Named palettes, formatting conventions, and a personality map for Excel workbooks. Use after the Design
Read (SKILL.md §5): pick a palette + personality, then apply consistently. Number-format discipline
(§12 + `references/financial_conventions.md`) is the other half — formatting carries meaning in spreadsheets.

## Header / Band Palettes

Roles: **Header fill** (column headers, section bands — white text on top), **Accent** (KPI highlights,
totals), **Zebra** (alternating row fill), **Text** (near-black body), **Negative** (loss/decline).

| Palette | Header fill | Accent | Zebra | Text | Negative | Reads as |
|---|---|---|---|---|---|---|
| Corporate Navy | `1F3864` | `2E74B5` | `F2F5FA` | `262626` | `C00000` | board deck, exec summary |
| Slate Analyst | `2E4057` | `1F8A70` | `F4F6F7` | `333333` | `C0392B` | financial model, analysis |
| Deep Indigo | `243F60` | `4472C4` | `EEF2F8` | `2B2B2B` | `BF360C` | KPI dashboard, ops tracker |
| Forest Ledger | `2C5F2D` | `97804F` | `F1F5F0` | `2D2D2D` | `B71C1C` | sustainability, grants |
| Graphite Minimal | `3A3A3A` | `0F6FC6` | `F5F5F5` | `262626` | `C62828` | clean modern tracker |

Rules: one Header fill dominates; one Accent only (KPI/totals); white text on dark headers (brightness
> 80%); zebra is subtle (≥ 95% lightness). Never rainbow conditional formatting — one color-scale / data-bar per metric.

## Formatting Conventions (carry meaning)

- **Numbers:** currency `#,##0` / accounting for ledgers; percent `0.0%`; negatives in parens `(1,234)`
  red; zero as `-`; thousands separators always. (See `financial_conventions.md`, incl. Korean 억/백만.)
- **Color coding (financial):** blue `0000FF` = hardcoded input · black `000000` = formula · green = link
  to another sheet · red = warning/negative.
- **Structure:** freeze the header row (`view`/panes); bold + filled header; column widths fit content
  (CJK ~2× Latin); group/outline for collapsible detail. No merged cells in data ranges (breaks sort/filter).

## Personality → Workbook Type

| Personality | Type | Palette + emphasis |
|---|---|---|
| Authoritative | board/exec summary | Corporate Navy · big KPI cards · sparklines · minimal grid |
| Rigorous / analytical | 3-statement / DCF model | Slate Analyst · blue-input/black-formula coding · scenario toggles |
| Operational | KPI dashboard, tracker | Deep Indigo · conditional formatting · data bars · pivot + slicers |
| Compliance / grant | budget, reporting | Forest Ledger · accounting format · audit-trail notes |
| Clean / modern | simple tracker | Graphite Minimal · one accent · generous row height |

## KPI / Dashboard layout
12-column mental grid; KPI cards top row (large number + small label); charts sized so axis labels don't
clip (`A5:L22` ≈ 12×18 for a 5-cat / 2-series column chart); ≥ 1 blank column/row between blocks.
