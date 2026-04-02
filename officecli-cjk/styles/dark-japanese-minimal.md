# Dark Japanese Minimal — Japanese Corporate

## Style Overview

A restrained, minimal dark style inspired by Japanese design aesthetics. Charcoal backgrounds with generous whitespace create a sense of calm authority. Red accent is used sparingly, echoing traditional Japanese design sensibility (和のデザイン). Typography centers on Yu Gothic for its clean proportions.

- **Scenario**: Japanese corporate presentations, strategy reviews, product launches
- **Mood**: Restrained, precise, authoritative
- **Tone**: Charcoal with subtle red accent
- **Language**: Japanese (日本語) primary, English secondary

## Color Palette

| Name           | Hex       | Usage                                    |
| -------------- | --------- | ---------------------------------------- |
| Background     | `#2D2D2D` | Charcoal, main background               |
| Surface        | `#3A3A3A` | Slightly lighter, card/section areas     |
| Primary Text   | `#F5F5F5` | Off-white, headings and body             |
| Secondary Text | `#AAAAAA` | Gray, captions and metadata              |
| Red Accent     | `#E53935` | Key metrics, alerts, CTA elements        |
| Muted Red      | `#4A2020` | Background tint for accent sections      |
| Border         | `#4A4A4A` | Subtle borders, dividers                 |
| White          | `#FFFFFF` | Pure white for emphasis only             |

## Typography

| Element           | Font             | Weight    | Size   |
| ----------------- | ---------------- | --------- | ------ |
| Title (Japanese)  | Yu Gothic        | Bold 700  | 32pt   |
| Title (Latin)     | Helvetica Neue   | Bold 700  | 32pt   |
| Subtitle          | Yu Gothic        | Medium    | 22pt   |
| Body (Japanese)   | Yu Gothic        | Regular   | 15pt   |
| Body (Latin)      | Helvetica Neue   | Regular   | 15pt   |
| Caption           | Yu Gothic        | Light     | 11pt   |
| Data / Numbers    | Helvetica Neue   | Light     | 44pt   |

### Font Fallback Chains

| Platform | Heading Chain                           | Body Chain                              |
| -------- | --------------------------------------- | --------------------------------------- |
| Windows  | Yu Gothic → Meiryo → MS Gothic         | Yu Gothic → Meiryo → MS PGothic        |
| macOS    | Yu Gothic → Hiragino Sans              | Hiragino Sans → Hiragino Kaku Gothic   |
| Linux    | Noto Sans JP → Noto Sans CJK JP        | Noto Sans JP → IPAGothic               |

## Typography Scale

```
Title:     32pt / 42pt line-height (1.31)
Subtitle:  22pt / 30pt line-height (1.36)
Body:      15pt / 26pt line-height (1.73)
Caption:   11pt / 18pt line-height (1.64)
Data:      44pt / 52pt line-height (1.18)
```

## OfficeCLI Commands

### Create minimal deck

```bash
officecli create strategy.pptx
officecli add strategy.pptx / --type slide --prop title="戦略レビュー"
officecli set strategy.pptx /slide[1] --prop background=2D2D2D
```

### Set title

```bash
officecli set strategy.pptx /slide[1]/shape[1] --prop \
  text="2025年度 事業戦略レビュー" \
  font="Yu Gothic" \
  font.size=32 \
  font.color=F5F5F5 \
  bold=true
```

### Add body text

```bash
officecli add strategy.pptx /slide[1] --type shape --prop \
  text="当四半期の売上高は前年同期比12%増の350億円となりました。特に、デジタルトランスフォーメーション事業が牽引し、営業利益率は前年比3ポイント改善しました。" \
  font="Yu Gothic" \
  font.size=15 \
  font.color=F5F5F5 \
  x=50 y=200 w=620 h=120
```

### Add red accent metric

```bash
officecli add strategy.pptx /slide[1] --type shape --prop \
  text="¥350億" \
  font="Helvetica Neue" \
  font.size=44 \
  font.color=E53935 \
  bold=true \
  x=50 y=340 w=200 h=70
```

### Add horizontal divider

```bash
officecli add strategy.pptx /slide[1] --type shape --prop \
  type=line \
  x=50 y=190 w=620 h=0 \
  line.color=4A4A4A \
  line.width=0.5
```

## Example Content (Japanese)

```
タイトル: 2025年度 事業戦略レビュー
サブタイトル: デジタルトランスフォーメーションによる持続的成長
本文: 当四半期の売上高は前年同期比12%増の350億円となりました。
     デジタル事業の成長率は28%に達し、全社売上の35%を占めています。
キャプション: ※ 本資料は2025年3月期第3四半期決算に基づきます。
```

## Design Notes

- Japanese design values "余白" (yohaku) — generous whitespace is intentional, not empty
- Red accent (#E53935) should appear in ≤3 elements per slide
- Avoid rounded corners — sharp edges align with the minimalist aesthetic
- Japanese text benefits from slightly wider line-height (1.7+) than Latin
- Kinsoku rules: ensure line-break prohibitions are respected (opening brackets, closing brackets, periods)
- CjkHelper.cs handles kinsoku via `IsKinsokuStart()` and `IsKinsokuEnd()` methods
