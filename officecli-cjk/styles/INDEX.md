# CJK Style Index — OfficeCLI Design System

> Merged design system: OfficeCLI's 51+ built-in styles + 6 CJK-optimized configurations.

## Quick Reference

| Style File | Target | Language | Background | Accent | Best For |
| --- | --- | --- | --- | --- | --- |
| [dark-korean-business.md](dark-korean-business.md) | Korean corporate | ko-KR | Navy `#1A1A2E` | Gold `#C9A96E` | Board decks, quarterly reports |
| [light-korean-academic.md](light-korean-academic.md) | Korean academic | ko-KR | White `#FFFFFF` | Blue `#2962FF` | Research, thesis defense |
| [dark-japanese-minimal.md](dark-japanese-minimal.md) | Japanese corporate | ja-JP | Charcoal `#2D2D2D` | Red `#E53935` | Strategy reviews, product launches |
| [light-chinese-modern.md](light-chinese-modern.md) | Chinese business | zh-CN | White `#FFFFFF` | Green `#00C853` | Market analysis, investor reports |
| [warm-korean-creative.md](warm-korean-creative.md) | Korean creative | ko-KR | Cream `#FFF8E1` | Coral/Teal | Marketing campaigns, startup pitches |
| [dark-cjk-tech.md](dark-cjk-tech.md) | Multi-CJK tech | ko/ja/zh | Dark `#0D1117` | Cyan/Purple | Tech talks, architecture reviews |

## How to Apply Styles via OfficeCLI

### Step 1: Create the deck

```bash
officecli create deck.pptx
officecli add deck.pptx / --type slide --prop title="제목"
```

### Step 2: Apply background color

```bash
officecli set deck.pptx /slide[1] --prop background=1A1A2E
```

### Step 3: Set fonts and colors per shape

```bash
officecli set deck.pptx /slide[1]/shape[1] --prop \
  font="Pretendard" \
  font.size=36 \
  font.color=C9A96E \
  bold=true
```

### Step 4: Batch apply to all slides

```bash
# Apply background to all slides
for i in $(seq 1 10); do
  officecli set deck.pptx /slide[$i] --prop background=1A1A2E
done
```

### CJK Auto-Detection

OfficeCLI's `CjkHelper` automatically detects CJK text and applies appropriate fonts when no explicit font is specified. The `BuildSegmentedRuns()` method splits mixed-script text into separate runs with correct font assignments.

Manual font override is recommended for consistent results:

```bash
# Explicit CJK font — always reliable
officecli set deck.pptx /slide[1]/shape[1] --prop font="Malgun Gothic" text="한국어 텍스트"

# Auto-detection — works but may vary by platform
officecli set deck.pptx /slide[1]/shape[1] --prop text="한국어 텍스트"
```

## Font Fallback Chains by Platform

### Korean (ko-KR)

| Platform | Heading | Body | Monospace |
| --- | --- | --- | --- |
| Windows | Pretendard → Malgun Gothic → 맑은 고딕 | Malgun Gothic → 맑은 고딕 → Segoe UI | D2Coding → Consolas |
| macOS | Pretendard → Apple SD Gothic Neo | Apple SD Gothic Neo → SF Pro | D2Coding → Menlo |
| Linux | Pretendard → Noto Sans KR | Noto Sans KR → DejaVu Sans | D2Coding → Noto Sans Mono CJK KR |

### Japanese (ja-JP)

| Platform | Heading | Body | Monospace |
| --- | --- | --- | --- |
| Windows | Yu Gothic → Meiryo → MS Gothic | Yu Gothic → Meiryo → MS PGothic | Sarasa Mono J → Consolas |
| macOS | Yu Gothic → Hiragino Sans | Hiragino Sans → Hiragino Kaku Gothic | Sarasa Mono J → Menlo |
| Linux | Noto Sans JP → Noto Sans CJK JP | Noto Sans JP → IPAGothic | Sarasa Mono J → Noto Sans Mono CJK JP |

### Chinese Simplified (zh-CN)

| Platform | Heading | Body | Monospace |
| --- | --- | --- | --- |
| Windows | Microsoft YaHei → SimHei → 黑体 | Microsoft YaHei → SimSun → 宋体 | Sarasa Mono SC → Consolas |
| macOS | PingFang SC → STHeiti → Heiti SC | PingFang SC → STSong → Songti SC | Sarasa Mono SC → Menlo |
| Linux | Noto Sans SC → Noto Sans CJK SC | Noto Sans SC → WenQuanYi Micro Hei | Sarasa Mono SC → Noto Sans Mono CJK SC |

## Relationship to OfficeCLI Built-in Styles

OfficeCLI ships with 51+ built-in styles in `officecli/styles/` organized by mood:

- **dark--** (20 styles): dark backgrounds, various accent colors
- **light--** (8 styles): clean white/light backgrounds
- **vivid--** (5 styles): bold, high-contrast palettes
- **warm--** (9 styles): earth tones, organic feel
- **bw--** (4 styles): black & white, typography-focused
- **mixed--** (4 styles): experimental, multi-palette

The 6 CJK styles in this directory are **supplementary configurations** that:
1. Define CJK-specific font pairings not covered by built-in styles
2. Provide platform-specific fallback chains
3. Include CJK typography scale adjustments (wider line-height)
4. Show officecli commands for CJK text rendering

They can be **combined** with any built-in style — use the built-in style's color palette with these CJK font configurations.

## CJK Typography Best Practices

1. **Line Height**: CJK text needs 1.6–1.8× line-height (vs 1.2–1.4 for Latin)
2. **Font Size**: Minimum 14pt for CJK body text (12pt is readable for Latin but cramped for CJK)
3. **Mixed Text**: Use `CjkHelper.SegmentText()` to split mixed-script runs
4. **Kinsoku**: Japanese text requires line-break prohibition rules (handled by `CjkHelper`)
5. **Numbers**: Use Latin fonts (Inter, Helvetica) for numbers in CJK text for consistent widths
