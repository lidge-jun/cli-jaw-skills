---
name: officecli-cjk
description: "CJK (Korean/Japanese/Chinese) text handling overlay for OfficeCLI. Ensures correct fonts, language tags, line-break rules, and encoding for East Asian documents."
metadata:
  openclaw:
    emoji: "🈶"
    requires: "officecli (>= 1.0.28)"
---

# officecli-cjk

Overlay skill for OfficeCLI that ensures correct CJK text rendering in DOCX, XLSX, and PPTX.
Use this skill when creating or modifying documents containing Korean, Japanese, or Chinese text.

> **Fork vs Upstream**: The upstream officecli binary ignores CJK fonts entirely.
> Our fork (`cli-jaw/officecli`) includes `CjkHelper.cs` which **auto-detects** CJK characters
> in text and applies the correct East Asian font, language tag, and kinsoku rules automatically.
> If using the upstream binary, you must apply these manually using the commands below.

---

## When to Use

- Document contains Korean (한글), Japanese (日本語), or Chinese (中文) text
- User requests Korean business report, Japanese presentation, or Chinese document
- Text appears garbled or fonts don't display correctly
- Line breaks occur in wrong places for CJK punctuation

---

## CJK Font Chains

Always set East Asian fonts when adding CJK text. Each language has a primary/fallback chain:

| Language | BCP 47 Tag | Windows Primary | Windows Fallback | macOS Fallback |
|----------|-----------|-----------------|------------------|----------------|
| Korean | `ko-KR` | Malgun Gothic | 맑은 고딕 | AppleSDGothicNeo |
| Japanese | `ja-JP` | Yu Gothic | Meiryo | Hiragino Sans |
| Chinese (Simplified) | `zh-CN` | Microsoft YaHei | SimSun | PingFang SC |
| Chinese (Traditional) | `zh-TW` | Microsoft JhengHei | MingLiU | PingFang TC |

**Cross-platform safe choice**: Pretendard (Korean), Noto Sans JP (Japanese), Noto Sans SC (Chinese).
These are freely available and render well on all platforms.

---

## DOCX Workflows

### Create a Korean Document

```bash
# Create and add Korean paragraphs
officecli create report.docx
officecli add report.docx /body --type paragraph \
  --prop text="분기별 매출 보고서" --prop style=Heading1
officecli add report.docx /body --type paragraph \
  --prop text="2026년 1분기 실적을 요약합니다."

# Verify text roundtrip
officecli view report.docx text
```

### Set CJK Font on Existing Runs

```bash
# Set East Asian font on a specific run
officecli set report.docx '/body/p[1]/r[1]' --prop font.name="Malgun Gothic"

# Batch font application across all runs
officecli batch report.docx --commands '[
  {"command":"set","path":"/body/p[1]/r[1]","props":{"font.name":"Malgun Gothic"}},
  {"command":"set","path":"/body/p[2]/r[1]","props":{"font.name":"Malgun Gothic"}}
]'
```

### Raw XML: East Asian Font and Language Tags

When the fork auto-detection isn't available, apply fonts and language tags via raw XML:

```bash
# Inspect current run properties
officecli get report.docx '/body/p[1]/r[1]' --json

# Set East Asian font via raw XML
officecli raw-set report.docx /document \
  --xpath '//w:r[w:t[contains(.,"분기")]]/w:rPr' \
  --action append \
  --xml '<w:rFonts w:eastAsia="Malgun Gothic" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'

# Set language tag for Korean spell-checking
officecli raw-set report.docx /document \
  --xpath '//w:r/w:rPr' \
  --action append \
  --xml '<w:lang w:eastAsia="ko-KR" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
```

### Verify CJK Tags in Raw XML

```bash
# Check that rFonts and lang elements exist
officecli raw report.docx /document | grep -E 'rFonts|w:lang'
```

---

## PPTX Workflows

### Create a Korean Presentation

```bash
officecli create slides.pptx
officecli add slides.pptx / --type slide
officecli add slides.pptx /slide[1] --type shape \
  --prop text="한국어 프레젠테이션" --prop x=1cm --prop y=1cm --prop w=8cm --prop h=1.5cm
officecli set slides.pptx '/slide[1]/shape[1]' --prop font="Malgun Gothic" --prop size=28

# Verify
officecli view slides.pptx text
```

### Japanese Slide Content

```bash
officecli add slides.pptx / --type slide
officecli add slides.pptx /slide[2] --type shape \
  --prop text="日本語のプレゼンテーション" --prop x=1cm --prop y=1cm --prop w=8cm --prop h=1.5cm
officecli set slides.pptx '/slide[2]/shape[1]' --prop font="Yu Gothic"
```

---

## XLSX Workflows

### Korean Column Headers

```bash
officecli create data.xlsx
officecli set data.xlsx /Sheet1/A1 --prop value="제품명"
officecli set data.xlsx /Sheet1/B1 --prop value="매출액"
officecli set data.xlsx /Sheet1/C1 --prop value="전년비"

# Apply CJK font to header row
officecli set data.xlsx '/Sheet1/A1:C1' --prop font.name="Malgun Gothic" --prop font.bold=true
```

### Chinese Data Entry

```bash
officecli set data.xlsx /Sheet1/A2 --prop value="冰箱"
officecli set data.xlsx /Sheet1/A3 --prop value="空调"
officecli set data.xlsx '/Sheet1/A2:A3' --prop font.name="Microsoft YaHei"
```

---

## Batch CJK Content (Multi-Language)

Create a document with Korean, Japanese, and Chinese sections in a single batch:

```bash
officecli create multilang.docx
officecli batch multilang.docx --commands '[
  {"command":"add","path":"/body","type":"paragraph","props":{"text":"한국어 섹션","style":"Heading1"}},
  {"command":"add","path":"/body","type":"paragraph","props":{"text":"한국 시장 분석 보고서입니다."}},
  {"command":"add","path":"/body","type":"paragraph","props":{"text":"日本語セクション","style":"Heading1"}},
  {"command":"add","path":"/body","type":"paragraph","props":{"text":"日本市場の分析レポートです。"}},
  {"command":"add","path":"/body","type":"paragraph","props":{"text":"中文部分","style":"Heading1"}},
  {"command":"add","path":"/body","type":"paragraph","props":{"text":"这是中国市场分析报告。"}}
]'

# Verify all three scripts rendered correctly
officecli view multilang.docx text
officecli validate multilang.docx
```

---

## Kinsoku (Line-Break Rules)

CJK text has special line-break rules called **kinsoku shori** (禁則処理).
OfficeCLI with `CjkHelper.cs` handles kinsoku automatically when CJK text is detected.

### Forbidden at Line Start (kinsoku: closing)

These characters must NOT appear at the beginning of a line:

```
! % ) , . : ; ? ] } 。 、 」 』 】 〕 ） ！ ％ ＞
？ ］ ： ； ー ～ っ ゃ ゅ ょ ぁ ぃ ぅ ぇ ぉ
```

### Forbidden at Line End (kinsoku: opening)

These characters must NOT appear at the end of a line:

```
( [ { 「 『 【 〔 （ ＜ ［
```

### How It Works

When `CjkHelper.DetectScript()` identifies CJK content, the handler:
1. Sets `w:kinsoku` attribute on paragraph properties (DOCX)
2. Applies `a:defRPr` with `lang` attribute (PPTX)
3. Ensures the rendering engine respects line-break rules

### Manual Kinsoku Check

```bash
# Inspect paragraph properties for kinsoku settings
officecli raw report.docx /document | grep kinsoku
# Look for: <w:kinsoku w:val="true"/>
```

---

## Language Tags (BCP 47)

Language tags are critical for:
- Spell-checking (right dictionary)
- Hyphenation rules
- Text-to-speech pronunciation
- CJK line-break behavior

| Language | BCP 47 | XML Element |
|----------|--------|-------------|
| Korean | `ko-KR` | `<w:lang w:eastAsia="ko-KR"/>` |
| Japanese | `ja-JP` | `<w:lang w:eastAsia="ja-JP"/>` |
| Chinese (Simplified) | `zh-CN` | `<w:lang w:eastAsia="zh-CN"/>` |
| Chinese (Traditional) | `zh-TW` | `<w:lang w:eastAsia="zh-TW"/>` |

### Document-Level Language Setting

```bash
# Set default language for entire DOCX document
officecli raw-set report.docx /styles \
  --xpath '//w:docDefaults/w:rPrDefault/w:rPr' \
  --action append \
  --xml '<w:lang w:eastAsia="ko-KR" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
```

---

## Encoding Recovery

### Symptoms of Encoding Issues

- Korean text displays as `¾Æ¹ö Áö` (EUC-KR interpreted as Latin)
- Japanese text shows `æ—¥æœ¬` (UTF-8 bytes shown as Latin)
- Square boxes `□□□` (missing font)
- Question marks `???` (encoding conversion failure)

### Diagnosis

```bash
# Check raw XML — UTF-8 text should be readable
officecli raw document.docx /document

# If garbled, check file encoding
file document.docx
# Should show: "Microsoft Word 2007+" or "Zip archive"

# Extract and inspect XML directly
officecli raw document.docx /document | head -5
# XML declaration should say encoding="UTF-8"
```

### Recovery: EUC-KR → UTF-8

If a legacy Korean document has EUC-KR encoded text embedded:

```bash
# 1. Export text content
officecli view document.docx text > content_raw.txt

# 2. Convert encoding (if needed outside officecli)
iconv -f EUC-KR -t UTF-8 content_raw.txt > content_utf8.txt

# 3. Create new document with correct encoding
officecli create recovered.docx
# Re-add content from converted text (line by line or batch)
```

### Recovery: Shift_JIS → UTF-8 (Japanese)

```bash
iconv -f SHIFT_JIS -t UTF-8 content_raw.txt > content_utf8.txt
```

### Prevention

- Always create documents with officecli (guarantees UTF-8)
- When importing external text, verify encoding first with `file` or `chardet`
- Our fork's `CjkHelper.cs` always writes UTF-8 XML

---

## CjkHelper.cs API Reference

The fork's `CjkHelper.cs` provides these auto-detection capabilities:

| Method | Purpose |
|--------|---------|
| `ContainsCjk(text)` | Returns `true` if text has any CJK characters |
| `DetectScript(text)` | Returns `Korean`, `Japanese`, `Chinese`, or `None` |
| `IsKorean(char)` | Hangul syllable/jamo range detection |
| `IsJapanese(char)` | Hiragana/Katakana range detection |
| `IsChinese(char)` | CJK Unified Ideographs detection |

When text is added via `officecli add`, the fork binary calls `DetectScript()` and automatically:
1. Sets `w:rFonts w:eastAsia` to the correct font chain
2. Adds `w:lang w:eastAsia` with the BCP 47 tag
3. Enables kinsoku processing for the paragraph

---

## Roundtrip Verification Checklist

After creating or modifying any CJK document, verify with this sequence:

```bash
# 1. Text content roundtrip — CJK characters should display correctly
officecli view document.docx text

# 2. Raw XML inspection — check font and language tags
officecli raw document.docx /document | grep -E 'rFonts|w:lang|eastAsia'

# 3. Schema validation — no structural errors
officecli validate document.docx

# 4. Layout check (PPTX only) — no text overflow
officecli check slides.pptx

# 5. Visual verification (if available)
# Open in LibreOffice/Word and confirm rendering
```

**Pass criteria:**
- [ ] `view text` shows all CJK characters correctly (no garbling)
- [ ] `raw` output contains `w:rFonts` with `eastAsia` attribute
- [ ] `raw` output contains `w:lang` with correct BCP 47 tag
- [ ] `validate` returns no errors
- [ ] `check` returns no text overflow warnings (PPTX)

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Create Korean doc | `officecli create report.docx && officecli add report.docx /body --type paragraph --prop text="한글 텍스트"` |
| Set CJK font | `officecli set file.docx '/body/p[1]/r[1]' --prop font.name="Malgun Gothic"` |
| Check font tags | `officecli raw file.docx /document \| grep rFonts` |
| Check lang tags | `officecli raw file.docx /document \| grep w:lang` |
| Validate | `officecli validate file.docx` |
| Multi-lang batch | `officecli batch file.docx --commands '[...]'` |
| PPTX CJK shape | `officecli set slides.pptx '/slide[1]/shape[1]' --prop font="Malgun Gothic"` |
| XLSX CJK header | `officecli set data.xlsx '/Sheet1/A1:C1' --prop font.name="Malgun Gothic"` |
