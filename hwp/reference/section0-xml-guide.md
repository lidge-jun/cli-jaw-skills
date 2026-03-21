# Section0.xml Writing Guide

XML reference for editing HWPX section content.

## Basic Paragraph

```xml
<hp:p paraPrIDRef="0" styleIDRef="0">
  <hp:run charPrIDRef="0">
    <hp:secPr><!-- ONLY in first paragraph, first run --></hp:secPr>
    <hp:t>Body text content.</hp:t>
  </hp:run>
</hp:p>
```

- `secPr`: first run of first paragraph only. Defines page size, margins, columns.
- `paraPrIDRef`: references paraPr ID defined in header.xml
- `charPrIDRef`: references charPr ID defined in header.xml

## Blank Line

```xml
<hp:p paraPrIDRef="0" styleIDRef="0">
  <hp:run charPrIDRef="0"><hp:t></hp:t></hp:run>
</hp:p>
```

## Mixed Formatting in One Paragraph

```xml
<hp:p paraPrIDRef="0" styleIDRef="0">
  <hp:run charPrIDRef="0"><hp:t>Normal </hp:t></hp:run>
  <hp:run charPrIDRef="7"><hp:t>Bold Title</hp:t></hp:run>
  <hp:run charPrIDRef="0"><hp:t> followed by normal text</hp:t></hp:run>
</hp:p>
```

## Table

```xml
<hp:tbl colCnt="2" rowCnt="2" cellSpacing="0" borderFillIDRef="1">
  <hp:tr>
    <hp:tc colAddr="0" rowAddr="0" colSpan="1" rowSpan="1">
      <hp:cellSz width="29764" height="1000"/>
      <hp:cellMargin left="510" right="510" top="141" bottom="141"/>
      <hp:p paraPrIDRef="0" styleIDRef="0">
        <hp:run charPrIDRef="0"><hp:t>Cell content</hp:t></hp:run>
      </hp:p>
    </hp:tc>
    <hp:tc colAddr="1" rowAddr="0" colSpan="1" rowSpan="1">
      <!-- ... -->
    </hp:tc>
  </hp:tr>
</hp:tbl>
```
