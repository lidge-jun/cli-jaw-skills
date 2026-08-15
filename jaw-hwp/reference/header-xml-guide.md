# Header.xml Modification Guide

Add new styles by appending definitions to header.xml.

## Adding charPr (Character Shape)

```xml
<hh:charPr id="7" height="2200" bold="true">
  <hh:fontRef hangul="맑은 고딕" latin="맑은 고딕"/>
</hh:charPr>
```

- `id`: next available number (existing max + 1)
- `height`: point size × 100 (22pt = 2200)

## Adding paraPr (Paragraph Shape)

```xml
<hh:paraPr id="20" align="CENTER">
  <hh:spacing line="160" lineType="PERCENT"/>
  <hh:margin left="0" right="0" indent="0"/>
</hh:paraPr>
```

## Adding borderFill

```xml
<hh:borderFill id="3">
  <hh:border>
    <hh:left type="SOLID" width="0.12mm" color="#000000"/>
    <hh:right type="SOLID" width="0.12mm" color="#000000"/>
    <hh:top type="SOLID" width="0.12mm" color="#000000"/>
    <hh:bottom type="SOLID" width="0.12mm" color="#000000"/>
  </hh:border>
</hh:borderFill>
```

## Template Style ID Summary

| Template | charPr | paraPr | borderFill |
|----------|--------|--------|------------|
| base | 0-6 | 0-19 | 1-2 |
| gonmun | +7-10 (title 22pt, signature 16pt, contact 8pt, table header 10pt) | +20-22 | +3-4 |
| report | +7-13 (title 20pt, subtitle 14pt, etc.) | +20-27 | +5 |
| minutes | +7-9 (title 18pt, section 12pt, table header 10pt) | +20-22 | +4 |
| proposal | +7-11 (title 20pt, subtitle 14pt, etc.) | +20-22 | +5-8 |

Full style ID maps: `style_id_maps.md`
