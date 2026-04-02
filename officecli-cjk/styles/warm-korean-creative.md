# Warm Korean Creative — Marketing & Creative

## Style Overview

A vibrant, warm style for Korean marketing and creative presentations. Cream backgrounds with coral and teal accents create an inviting, energetic mood. Cafe24 Ssurround headings add personality while Pretendard body text maintains readability.

- **Scenario**: Marketing campaigns, creative briefs, brand storytelling, startup pitches
- **Mood**: Energetic, playful, inviting
- **Tone**: Warm cream with coral and teal pops
- **Language**: Korean (한국어) primary, English secondary

## Color Palette

| Name           | Hex       | Usage                                  |
| -------------- | --------- | -------------------------------------- |
| Background     | `#FFF8E1` | Warm cream, main background            |
| Surface        | `#FFFFFF` | Pure white, card backgrounds           |
| Primary Text   | `#2D2D2D` | Near-black, body text                  |
| Heading Text   | `#1A1A1A` | Dark, headings                         |
| Coral           | `#FF6B6B` | Primary accent, CTAs, highlights       |
| Coral Dark     | `#D84315` | Hover states, emphasis                 |
| Teal           | `#00BFA5` | Secondary accent, success, charts      |
| Teal Light     | `#E0F2F1` | Tinted backgrounds for teal sections   |
| Coral Light    | `#FFEBEE` | Tinted backgrounds for coral sections  |
| Border         | `#E0D5C0` | Warm-toned borders                     |

## Typography

| Element          | Font              | Weight    | Size   |
| ---------------- | ----------------- | --------- | ------ |
| Title (Korean)   | Cafe24 Ssurround  | Bold      | 36pt   |
| Title (Latin)    | Poppins           | Bold 700  | 36pt   |
| Subtitle         | Pretendard        | SemiBold  | 22pt   |
| Body (Korean)    | Pretendard        | Regular   | 15pt   |
| Body (Latin)     | Inter             | Regular   | 15pt   |
| Caption          | Pretendard        | Regular   | 11pt   |
| Accent Text      | Cafe24 Ssurround  | Regular   | 20pt   |

### Font Fallback Chains

| Platform | Heading Chain                                  | Body Chain                               |
| -------- | ---------------------------------------------- | ---------------------------------------- |
| Windows  | Cafe24 Ssurround → Malgun Gothic → 맑은 고딕  | Pretendard → Malgun Gothic → 맑은 고딕   |
| macOS    | Cafe24 Ssurround → Apple SD Gothic Neo         | Pretendard → Apple SD Gothic Neo         |
| Linux    | Cafe24 Ssurround → Noto Sans KR               | Pretendard → Noto Sans KR               |

> **Note**: Cafe24 Ssurround is a free font from Cafe24 (cafe24.com/fonts). It must be installed on the rendering machine. If unavailable, falls back to system CJK font.

## Typography Scale

```
Title:     36pt / 46pt line-height (1.28)
Subtitle:  22pt / 30pt line-height (1.36)
Body:      15pt / 26pt line-height (1.73)
Caption:   11pt / 18pt line-height (1.64)
Accent:    20pt / 28pt line-height (1.40)
```

## OfficeCLI Commands

### Create creative deck

```bash
officecli create campaign.pptx
officecli add campaign.pptx / --type slide --prop title="브랜드 캠페인"
officecli set campaign.pptx /slide[1] --prop background=FFF8E1
```

### Set playful title

```bash
officecli set campaign.pptx /slide[1]/shape[1] --prop \
  text="우리가 만드는 새로운 경험 ✨" \
  font="Cafe24 Ssurround" \
  font.size=36 \
  font.color=1A1A1A \
  bold=true
```

### Add body text

```bash
officecli add campaign.pptx /slide[1] --type shape --prop \
  text="Z세대 소비자를 위한 새로운 브랜드 경험을 설계합니다. 감각적인 비주얼과 진정성 있는 스토리텔링으로 브랜드 가치를 전달합니다." \
  font="Pretendard" \
  font.size=15 \
  font.color=2D2D2D \
  x=50 y=200 w=620 h=100
```

### Add coral accent CTA

```bash
officecli add campaign.pptx /slide[1] --type shape --prop \
  text="지금 시작하기" \
  font="Pretendard" \
  font.size=18 \
  font.color=FFFFFF \
  fill=FF6B6B \
  bold=true \
  x=250 y=380 w=220 h=50
```

### Add teal metric

```bash
officecli add campaign.pptx /slide[1] --type shape --prop \
  text="DAU 2.3M" \
  font="Poppins" \
  font.size=40 \
  font.color=00BFA5 \
  bold=true \
  x=50 y=320 w=200 h=60
```

## Example Content (Korean)

```
제목: 우리가 만드는 새로운 경험 ✨
부제: 2025 봄 시즌 브랜드 캠페인
본문: Z세대 소비자의 마음을 사로잡는 건 화려한 광고가 아닙니다.
     진정성 있는 스토리와 공감할 수 있는 경험이 핵심입니다.
     이번 캠페인은 "일상 속 작은 행복"을 테마로,
     소비자 참여형 콘텐츠를 중심으로 전개합니다.
CTA: 캠페인 참여하기 →
```

## Design Notes

- Creative decks allow more personality — Cafe24 Ssurround adds Korean character
- Coral (#FF6B6B) and Teal (#00BFA5) should be balanced — don't let one dominate
- Warm cream background (#FFF8E1) is easier on eyes than pure white for long presentations
- Use emoji sparingly in titles (✨, 🎯, 💡) — acceptable in creative contexts
- Card-style layouts with white (#FFFFFF) surfaces on cream background create depth
- Cafe24 Ssurround is a display font — do NOT use it below 18pt
