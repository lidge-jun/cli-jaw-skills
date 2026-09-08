# docx-js API Reference

Detailed API examples for the `docx` npm package.

## Styles

```typescript
const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }  // 12pt (size = half-points)
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1",
        basedOn: "Normal", next: "Normal",
        quickFormat: true,
        run: { size: 56, bold: true, color: "000000" },  // 28pt
        paragraph: { spacing: { after: 120 } }
      }
    ]
  },
  sections: [{ children: [
    new Paragraph({ style: "Heading1", children: [new TextRun("Title")] })
  ]}]
});
```

> `size` uses **half-point** units — 12pt = `size: 24`

## Bullet & Numbered Lists

```typescript
import { LevelFormat, AlignmentType, convertInchesToTwip } from "docx";

const doc = new Document({
  numbering: {
    config: [{
      reference: "my-bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: {
          paragraph: {
            indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.25) }
          }
        }
      }]
    }]
  },
  sections: [{
    children: [
      new Paragraph({
        numbering: { reference: "my-bullets", level: 0 },
        children: [new TextRun("First item")]
      }),
      new Paragraph({
        numbering: { reference: "my-bullets", level: 0 },
        children: [new TextRun("Second item")]
      })
    ]
  }]
});
```

Use numbering config for bullets — manual `"• Item"` strings break Word's list feature.

## Tables

```typescript
import { Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType } from "docx";

const table = new Table({
  columnWidths: [3505, 5505],  // DXA
  rows: [
    new TableRow({
      children: [
        new TableCell({
          width: { size: 3505, type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: "4472C4" },
          children: [new Paragraph("Header")]
        }),
        new TableCell({
          width: { size: 5505, type: WidthType.DXA },
          shading: { type: ShadingType.CLEAR, color: "auto", fill: "4472C4" },
          children: [new Paragraph("Value")]
        })
      ]
    })
  ]
});
```

- Use `ShadingType.CLEAR` — `SOLID` causes black background
- Use `WidthType.DXA` — percentage breaks in Google Docs

## Table of Contents

```typescript
import { TableOfContents, HeadingLevel } from "docx";

new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" })

// Heading paragraphs require outlineLevel in style definition:
paragraphStyles: [{
  id: "Heading1", name: "Heading 1",
  paragraph: { outlineLevel: 0 },  // required for TOC
}]
```

## Header & Footer

```typescript
import { Header, Footer, PageNumber } from "docx";

const doc = new Document({
  sections: [{
    properties: { titlePage: true },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun("Title "),
            new TextRun({ children: ["Page ", PageNumber.CURRENT] })
          ]
        })]
      }),
      first: new Header({
        children: [new Paragraph({ children: [new TextRun("First Page Header")] })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({
            children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES]
          })]
        })]
      })
    },
    children: [new Paragraph("Content")]
  }]
});
```

## Images via XML (OOXML)

1. Add image file to `word/media/`
2. Add relationship to `word/_rels/document.xml.rels`:
```xml
<Relationship Id="rId5" Type=".../image" Target="media/image1.png"/>
```
3. Add content type to `[Content_Types].xml`:
```xml
<Default Extension="png" ContentType="image/png"/>
```
4. Reference in document.xml (EMU units: 914400 = 1 inch):
```xml
<w:drawing>
  <wp:inline>
    <wp:extent cx="914400" cy="914400"/>
    <a:graphic>
      <a:graphicData uri=".../picture">
        <pic:pic>
          <pic:blipFill><a:blip r:embed="rId5"/></pic:blipFill>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing>
```

## Relationships Editing

- Manage `rId` mappings in `_rels/document.xml.rels`
- When replacing images: update both `media/` file and `_rels` simultaneously
- For new rId: use existing max number + 1
