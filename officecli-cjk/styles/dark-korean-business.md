# Dark Korean Business — Corporate Reports

## Style Overview

A premium corporate style optimized for Korean business presentations. Deep navy backgrounds with gold accents convey authority and trustworthiness. Typography pairs Pretendard headings with Malgun Gothic body text for maximum readability on projectors and screens.

- **Scenario**: Corporate reports, board decks, quarterly reviews, executive summaries
- **Mood**: Authoritative, refined, premium
- **Tone**: Deep navy with warm gold accents
- **Language**: Korean (한국어) primary, English secondary

## Color Palette

| Name           | Hex       | Usage                              |
| -------------- | --------- | ---------------------------------- |
| Background     | `#1A1A2E` | Deep navy, main background         |
| Surface        | `#16213E` | Slightly lighter, card backgrounds |
| Gold Accent    | `#C9A96E` | Headings, dividers, key numbers    |
| Primary Text   | `#FFFFFF` | White, headings and titles         |
| Secondary Text | `#B0B0C0` | Body text, descriptions            |
| Border         | `#2A2A4E` | Subtle borders, separators         |
| Success        | `#4CAF50` | Positive metrics                   |
| Danger         | `#E53935` | Negative metrics, warnings         |

## Typography

| Element          | Font             | Weight    | Size   |
| ---------------- | ---------------- | --------- | ------ |
| Title (Korean)   | Pretendard       | Bold 700  | 36pt   |
| Title (Latin)    | Inter             | Bold 700  | 36pt   |
| Subtitle         | Pretendard       | Medium 500| 24pt   |
| Body (Korean)    | Malgun Gothic    | Regular   | 16pt   |
| Body (Latin)     | Segoe UI         | Regular   | 16pt   |
| Caption          | Malgun Gothic    | Regular   | 12pt   |
| Data / Numbers   | Inter             | SemiBold  | 48pt   |

### Font Fallback Chains

| Platform | Heading Chain                          | Body Chain                              |
| -------- | -------------------------------------- | --------------------------------------- |
| Windows  | Pretendard → Malgun Gothic → 맑은 고딕 | Malgun Gothic → 맑은 고딕 → Segoe UI   |
| macOS    | Pretendard → Apple SD Gothic Neo       | Apple SD Gothic Neo → SF Pro            |
| Linux    | Pretendard → Noto Sans KR              | Noto Sans KR → DejaVu Sans             |

## Typography Scale

```
Title:     36pt / 44pt line-height (1.22)
Subtitle:  24pt / 32pt line-height (1.33)
Body:      16pt / 26pt line-height (1.63)
Caption:   12pt / 18pt line-height (1.50)
Data:      48pt / 56pt line-height (1.17)
```

## OfficeCLI Commands

### Create and apply background

```bash
officecli create report.pptx
officecli add report.pptx / --type slide --prop title="2025년 실적 보고"
officecli set report.pptx /slide[1] --prop background=1A1A2E
```

### Set title with CJK font

```bash
officecli set report.pptx /slide[1]/shape[1] --prop \
  text="2025년 4분기 실적 보고" \
  font="Pretendard" \
  font.size=36 \
  font.color=C9A96E \
  bold=true
```

### Add body text

```bash
officecli add report.pptx /slide[1] --type shape --prop \
  text="매출액은 전년 대비 25% 증가하였으며, 영업이익률은 15.3%를 달성했습니다." \
  font="Malgun Gothic" \
  font.size=16 \
  font.color=B0B0C0 \
  x=50 y=200 w=620 h=100
```

### Add metric card

```bash
officecli add report.pptx /slide[1] --type shape --prop \
  text="₩2.5조" \
  font="Inter" \
  font.size=48 \
  font.color=C9A96E \
  bold=true \
  x=50 y=320 w=200 h=80
```

## Example Content (Korean)

```
제목: 2025년 4분기 실적 보고
부제: 지속 가능한 성장을 위한 전략 수립
본문: 올해 당사는 매출 2조 5천억 원을 달성하며 전년 대비 25% 성장을 기록했습니다.
     영업이익은 3,825억 원으로 영업이익률 15.3%를 기록했습니다.
캡션: * 본 자료는 K-IFRS 연결 기준입니다.
```

## Design Notes

- Gold accent (#C9A96E) should be used sparingly — titles, key metrics, and dividers only
- Body text uses lighter gray (#B0B0C0) to reduce eye strain on dark backgrounds
- Korean text requires wider line-height (1.6+) than Latin text for readability
- Number-heavy slides should use Inter for consistent numeral widths
- Avoid small text (<14pt) for Korean on dark backgrounds
