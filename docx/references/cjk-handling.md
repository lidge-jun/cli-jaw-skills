# CJK / Korean Text Handling

## Word Wrapping

Korean uses syllable-level wrapping. Set OOXML attributes on paragraphs:

```xml
<w:pPr>
  <w:wordWrap w:val="0"/>        <!-- Allow character-level wrapping -->
  <w:overflowPunct w:val="1"/>   <!-- Kinsoku: prevent punctuation at line start -->
  <w:autoSpaceDE w:val="1"/>     <!-- Auto 1/4em gap between Latin and Korean -->
  <w:autoSpaceDN w:val="1"/>     <!-- Auto gap between Korean and digits -->
</w:pPr>
```

| Attribute                 | Default | Effect                                                       |
| ------------------------- | ------- | ------------------------------------------------------------ |
| `w:wordWrap val="0"`      | 1       | Allow syllable-level wrapping (essential for narrow columns) |
| `w:overflowPunct val="1"` | 1       | Kinsoku shori — keeps closing punctuation off line starts    |
| `w:autoSpaceDE val="1"`   | 1       | Automatic spacing between Korean and Latin text              |
| `w:autoSpaceDN val="1"`   | 1       | Automatic spacing between Korean and digits                  |

> docx-js doesn't expose these attributes directly. Generate the document, then use the unpack → XML edit → pack workflow to inject them.

## East Asian Fonts

```typescript
// docx-js: specify EA font in TextRun
new TextRun({
  text: "한글 문서",
  font: { eastAsia: "Malgun Gothic" }
});

// Document-level default
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Noto Sans KR", size: 24 }  // 12pt
      }
    }
  },
});
```

### Recommended Korean Fonts

| Font          | License   | Cross-platform | Best for          |
| ------------- | --------- | -------------- | ----------------- |
| Noto Sans KR  | OFL       | Win/Mac/Linux  | Safest choice     |
| Pretendard    | OFL       | Win/Mac/Linux  | Modern UI         |
| Malgun Gothic | MS bundle | Windows only   | Windows-only docs |
| NanumGothic   | OFL       | Win/Mac/Linux  | General Korean    |
| Noto Serif KR | OFL       | Win/Mac/Linux  | Print/academic    |

## DXA Width for CJK

CJK characters occupy roughly twice the width of Latin characters. Use `scripts/ooxml/cjk_utils.py`:

```python
from scripts.ooxml.cjk_utils import get_display_width, pixel_to_emu, emu_to_pixel

get_display_width("Hello")     # 5
get_display_width("한글 테스트")  # 10

pixel_to_emu(400)              # 3810000
emu_to_pixel(3810000)          # 400
```

Table column width estimation:

```typescript
const columnWidths = headers.map(h => {
  const displayWidth = [...h].reduce((sum, ch) => {
    const code = ch.codePointAt(0) ?? 0;
    return sum + ((code >= 0xAC00 && code <= 0xD7AF) ||
                  (code >= 0x3000 && code <= 0x9FFF) ? 2 : 1);
  }, 0);
  return Math.max(displayWidth * 180, 1440);  // 180 DXA per char unit, min 1 inch
});
```

## Korean Language Injection (Post-processing)

Inject `lang="ko-KR"` for proper kinsoku and spell-check:

```bash
python scripts/ooxml/unpack.py output.docx unpacked/
python -c "from scripts.ooxml.cjk_utils import inject_korean_lang; inject_korean_lang('unpacked/')"
python scripts/ooxml/pack.py unpacked/ output_ko.docx --original output.docx
```

## Accessibility for CJK

| Requirement       | Standard          | Implementation                                  |
| ----------------- | ----------------- | ----------------------------------------------- |
| Color contrast    | >= 4.5:1          | Use `cjk_utils.check_contrast()` to verify      |
| Image alt text    | Required on all   | `ImageRun({ altText: { title, description } })` |
| Minimum font size | >= 10pt           | No captions below 10pt                          |
| Language metadata | `lang="ko-KR"`    | Enables screen reader pronunciation             |
| Heading hierarchy | Sequential levels | H1 → H2 → H3, no skipping                       |

```typescript
// Alt text on images
new ImageRun({
  type: "png", data: imageData,
  transformation: { width: 400, height: 300 },
  altText: {
    title: "Sales Chart",
    description: "Bar chart showing Q1-Q4 2025 revenue growth"
  }
});
```

```python
# Contrast check
from scripts.ooxml.cjk_utils import check_contrast
ratio = check_contrast("FFFFFF", "4472C4")
assert ratio >= 4.5, f"Contrast insufficient: {ratio:.1f}:1 (need >= 4.5:1)"
```
