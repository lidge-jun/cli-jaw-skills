# Light Chinese Modern — Chinese Business

## Style Overview

A bright, modern style for Chinese business presentations. Clean white backgrounds with a distinctive green accent convey innovation and growth. Typography pairs Microsoft YaHei headings with PingFang SC body text for cross-platform readability.

- **Scenario**: Chinese business presentations, product launches, market analysis, investor reports
- **Mood**: Modern, innovative, forward-looking
- **Tone**: Clean white with vibrant green accent
- **Language**: Simplified Chinese (简体中文) primary, English secondary

## Color Palette

| Name           | Hex       | Usage                                |
| -------------- | --------- | ------------------------------------ |
| Background     | `#FFFFFF` | Pure white, main background          |
| Surface        | `#F0F4F0` | Light green-tinted gray, sections    |
| Primary Text   | `#1A1A1A` | Near-black, headings and body        |
| Secondary Text | `#666666` | Gray, descriptions and captions      |
| Green Accent   | `#00C853` | Key metrics, CTAs, highlights        |
| Green Dark     | `#00962F` | Hover/active states, emphasis        |
| Green Light    | `#E8F5E9` | Background tint for accent areas     |
| Border         | `#E0E0E0` | Table borders, dividers              |
| Danger         | `#D32F2F` | Negative metrics, warnings           |

## Typography

| Element          | Font             | Weight    | Size   |
| ---------------- | ---------------- | --------- | ------ |
| Title (Chinese)  | Microsoft YaHei  | Bold 700  | 34pt   |
| Title (Latin)    | Helvetica Neue   | Bold 700  | 34pt   |
| Subtitle         | Microsoft YaHei  | Regular   | 22pt   |
| Body (Chinese)   | PingFang SC      | Regular   | 15pt   |
| Body (Latin)     | Helvetica Neue   | Regular   | 15pt   |
| Caption          | PingFang SC      | Light     | 11pt   |
| Data / Numbers   | DIN Next         | Medium    | 48pt   |

### Font Fallback Chains

| Platform | Heading Chain                              | Body Chain                                  |
| -------- | ------------------------------------------ | ------------------------------------------- |
| Windows  | Microsoft YaHei → SimHei → 黑体           | Microsoft YaHei → SimSun → 宋体            |
| macOS    | PingFang SC → STHeiti → Heiti SC           | PingFang SC → STSong → Songti SC           |
| Linux    | Noto Sans SC → Noto Sans CJK SC → WenQuanYi | Noto Sans SC → WenQuanYi Micro Hei        |

## Typography Scale

```
Title:     34pt / 44pt line-height (1.29)
Subtitle:  22pt / 30pt line-height (1.36)
Body:      15pt / 26pt line-height (1.73)
Caption:   11pt / 18pt line-height (1.64)
Data:      48pt / 56pt line-height (1.17)
```

## OfficeCLI Commands

### Create business deck

```bash
officecli create market.pptx
officecli add market.pptx / --type slide --prop title="市场分析报告"
officecli set market.pptx /slide[1] --prop background=FFFFFF
```

### Set title

```bash
officecli set market.pptx /slide[1]/shape[1] --prop \
  text="2025年中国市场分析报告" \
  font="Microsoft YaHei" \
  font.size=34 \
  font.color=1A1A1A \
  bold=true
```

### Add body text

```bash
officecli add market.pptx /slide[1] --type shape --prop \
  text="中国数字经济市场规模预计将在2025年达到50万亿元人民币，年增长率保持在15%以上。人工智能和云计算是主要增长引擎。" \
  font="PingFang SC" \
  font.size=15 \
  font.color=1A1A1A \
  x=50 y=200 w=620 h=120
```

### Add green accent metric

```bash
officecli add market.pptx /slide[1] --type shape --prop \
  text="¥50万亿" \
  font="DIN Next" \
  font.size=48 \
  font.color=00C853 \
  bold=true \
  x=50 y=340 w=250 h=80
```

### Add accent section background

```bash
officecli add market.pptx /slide[1] --type shape --prop \
  type=rectangle \
  fill=E8F5E9 \
  x=40 y=160 w=640 h=280 \
  line.color=00C853 \
  line.width=1
```

## Example Content (Simplified Chinese)

```
标题: 2025年中国市场分析报告
副标题: 数字经济时代的战略机遇与挑战
正文: 中国数字经济市场规模预计将在2025年达到50万亿元人民币。
     人工智能、云计算和大数据是推动增长的三大引擎。
     企业数字化转型已从可选项变为必选项。
注释: * 数据来源：中国信息通信研究院《中国数字经济发展报告》
```

## Design Notes

- Chinese characters are visually denser than Latin — use generous spacing
- Green (#00C853) conveys growth and prosperity in Chinese business culture
- Avoid excessive red in financial contexts unless showing positive gains (red = gain in Chinese markets)
- PingFang SC provides excellent screen rendering on macOS/iOS
- Microsoft YaHei is the standard CJK UI font on Windows — safe default
- Body text line-height should be ≥1.7 for dense Chinese paragraphs
- Numbers and percentages should use Latin fonts (DIN, Helvetica) for consistent width
