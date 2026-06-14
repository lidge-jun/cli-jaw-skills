# CJK Text Handling Reference (officecli)

Cross-format reference for Korean, Japanese, and Chinese text handling in OOXML documents.
Applicable to DOCX, XLSX, and PPTX. Format-specific commands live in each format's SKILL.md.

> **Fork vs Upstream**: The upstream officecli binary ignores CJK fonts.
> Our fork (`https://github.com/lidge-jun/OfficeCLI`) includes `CjkHelper.cs` which **auto-detects** CJK characters
> and applies the correct East Asian font, language tag, and kinsoku rules automatically.

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

---

## BCP 47 Language Tags

Language tags are critical for spell-checking, hyphenation, TTS pronunciation, and CJK line-break behavior.

| Language | BCP 47 | DOCX XML Element | PPTX DrawingML |
|----------|--------|-------------------|----------------|
| Korean | `ko-KR` | `<w:lang w:eastAsia="ko-KR"/>` | `<a:ea typeface="Malgun Gothic"/>` + `lang="ko-KR"` |
| Japanese | `ja-JP` | `<w:lang w:eastAsia="ja-JP"/>` | `<a:ea typeface="Yu Gothic"/>` + `lang="ja-JP"` |
| Chinese (Simplified) | `zh-CN` | `<w:lang w:eastAsia="zh-CN"/>` | `<a:ea typeface="Microsoft YaHei"/>` + `lang="zh-CN"` |
| Chinese (Traditional) | `zh-TW` | `<w:lang w:eastAsia="zh-TW"/>` | `<a:ea typeface="Microsoft JhengHei"/>` + `lang="zh-TW"` |

### Document-Level Language Setting (DOCX)

```bash
officecli raw-set report.docx /styles \
  --xpath '//w:docDefaults/w:rPrDefault/w:rPr' \
  --action append \
  --xml '<w:lang w:eastAsia="ko-KR" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
```

---

## Kinsoku (Line-Break Rules)

CJK text has special line-break rules called **kinsoku shori** (禁則処理).
The fork's `CjkHelper.cs` handles kinsoku automatically when CJK text is detected.

### Forbidden at Line Start (closing)

```
! % ) , . : ; ? ] } 。 、 」 』 】 〕 ） ！ ％ ＞
？ ］ ： ； ー ～ っ ゃ ゅ ょ ぁ ぃ ぅ ぇ ぉ
```

### Forbidden at Line End (opening)

```
( [ { 「 『 【 〔 （ ＜ ［
```

### How It Works

When `CjkHelper.DetectScript()` identifies CJK content:
1. Sets `w:kinsoku` attribute on paragraph properties (DOCX)
2. Applies `a:defRPr` with `lang` attribute (PPTX)
3. Ensures the rendering engine respects line-break rules

---

## Encoding Recovery

### Symptoms

- Korean: `¾Æ¹ö Áö` (EUC-KR interpreted as Latin)
- Japanese: `æ—¥æœ¬` (UTF-8 bytes shown as Latin)
- Square boxes `□□□` (missing font)
- Question marks `???` (encoding conversion failure)

### Diagnosis

```bash
officecli raw document.docx /document
file document.docx
officecli raw document.docx /document | head -5
```

### Recovery: EUC-KR → UTF-8

```bash
officecli view document.docx text > content_raw.txt
iconv -f EUC-KR -t UTF-8 content_raw.txt > content_utf8.txt
officecli create recovered.docx
# Re-add content from converted text
```

### Recovery: Shift_JIS → UTF-8 (Japanese)

```bash
iconv -f SHIFT_JIS -t UTF-8 content_raw.txt > content_utf8.txt
```

### Prevention

- Always create documents with officecli (guarantees UTF-8)
- When importing external text, verify encoding first with `file` or `chardet`
- The fork's `CjkHelper.cs` always writes UTF-8 XML

---

## CjkHelper.cs API Reference

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

## Batch CJK Content (Multi-Language)

```bash
officecli create multilang.docx
officecli batch multilang.docx --commands '[
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"한국어 섹션","style":"Heading1"}},
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"한국 시장 분석 보고서입니다."}},
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"日本語セクション","style":"Heading1"}},
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"日本市場の分析レポートです。"}},
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"中文部分","style":"Heading1"}},
  {"command":"add","parent":"/body","type":"paragraph","props":{"text":"这是中国市场分析报告。"}}
]'
```

---

## Roundtrip Verification Checklist

```bash
officecli view document.docx text          # CJK characters display correctly
officecli raw document.docx /document | grep -E 'rFonts|w:lang|eastAsia'
officecli validate document.docx           # No structural errors
officecli validate slides.pptx             # PPTX structural/schema check
officecli view slides.pptx issues          # PPTX layout/content issue probe
officecli view slides.pptx stats           # Font usage and document statistics
```

**Pass criteria:**
- [ ] `view text` shows all CJK characters correctly
- [ ] `raw` output contains `w:rFonts` with `eastAsia` attribute
- [ ] `raw` output contains `w:lang` with correct BCP 47 tag
- [ ] `validate` returns no errors

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Set CJK font | `officecli set file '/path' --prop font.name="Malgun Gothic"` |
| Check font tags | `officecli raw file /document \| grep rFonts` |
| Check lang tags | `officecli raw file /document \| grep w:lang` |
| Validate | `officecli validate file` |
| PPTX issue probe | `officecli view slides.pptx issues` |
| Multi-lang batch | `officecli batch file --commands '[...]'` |
| PPTX CJK shape | `officecli set slides.pptx '/slide[1]/shape[1]' --prop font="Malgun Gothic"` |
| XLSX CJK header | `officecli set data.xlsx '/Sheet1/A1:C1' --prop font.name="Malgun Gothic"` |
