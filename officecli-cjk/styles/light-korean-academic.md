# Light Korean Academic — Research & Academic

## Style Overview

A clean, professional style for Korean academic and research presentations. White backgrounds with minimal accents ensure content legibility. Typography uses Noto Sans KR for its excellent Unicode coverage and balanced CJK proportions.

- **Scenario**: Research presentations, thesis defense, academic conferences, lectures
- **Mood**: Clean, scholarly, authoritative
- **Tone**: White background, dark text, blue accent
- **Language**: Korean (한국어) primary, English secondary

## Color Palette

| Name           | Hex       | Usage                              |
| -------------- | --------- | ---------------------------------- |
| Background     | `#FFFFFF` | Pure white, main background        |
| Surface        | `#F5F7FA` | Light gray, section backgrounds    |
| Primary Text   | `#2D2D2D` | Near-black, headings and body      |
| Secondary Text | `#666666` | Gray, captions and footnotes       |
| Accent Blue    | `#2962FF` | Links, key terms, chart primary    |
| Accent Light   | `#E3F2FD` | Highlighted sections, callouts     |
| Border         | `#E0E0E0` | Table borders, separators          |
| Success        | `#2E7D32` | Positive results                   |
| Warning        | `#F57F17` | Cautions, limitations              |

## Typography

| Element          | Font             | Weight    | Size   |
| ---------------- | ---------------- | --------- | ------ |
| Title (Korean)   | Noto Sans KR     | Bold 700  | 32pt   |
| Title (Latin)    | Noto Sans        | Bold 700  | 32pt   |
| Subtitle         | Noto Sans KR     | Medium 500| 20pt   |
| Body (Korean)    | Malgun Gothic    | Regular   | 14pt   |
| Body (Latin)     | Noto Sans        | Regular   | 14pt   |
| Caption/Footnote | Noto Sans KR     | Regular   | 10pt   |
| Code             | D2Coding         | Regular   | 12pt   |

### Font Fallback Chains

| Platform | Heading Chain                           | Body Chain                              |
| -------- | --------------------------------------- | --------------------------------------- |
| Windows  | Noto Sans KR → Malgun Gothic           | Malgun Gothic → 맑은 고딕 → Arial      |
| macOS    | Noto Sans KR → Apple SD Gothic Neo     | Apple SD Gothic Neo → Helvetica Neue    |
| Linux    | Noto Sans KR → NanumGothic             | Noto Sans KR → DejaVu Sans             |

## Typography Scale

```
Title:     32pt / 40pt line-height (1.25)
Subtitle:  20pt / 28pt line-height (1.40)
Body:      14pt / 24pt line-height (1.71)
Caption:   10pt / 16pt line-height (1.60)
Code:      12pt / 20pt line-height (1.67)
```

## OfficeCLI Commands

### Create academic deck

```bash
officecli create thesis.pptx
officecli add thesis.pptx / --type slide --prop title="연구 결과 발표"
officecli set thesis.pptx /slide[1] --prop background=FFFFFF
```

### Set title

```bash
officecli set thesis.pptx /slide[1]/shape[1] --prop \
  text="한국어 자연어 처리에서의 형태소 분석 개선 방안" \
  font="Noto Sans KR" \
  font.size=32 \
  font.color=2D2D2D \
  bold=true
```

### Add body with citations

```bash
officecli add thesis.pptx /slide[1] --type shape --prop \
  text="본 연구에서는 Transformer 기반의 형태소 분석기를 제안한다 (Kim et al., 2024). 기존 방법 대비 F1 스코어가 2.3%p 향상되었다." \
  font="Malgun Gothic" \
  font.size=14 \
  font.color=2D2D2D \
  x=50 y=180 w=620 h=120
```

### Add code block

```bash
officecli add thesis.pptx /slide[1] --type shape --prop \
  text="from konlpy.tag import Mecab\nmecab = Mecab()\nresult = mecab.morphs('한국어 형태소 분석')" \
  font="D2Coding" \
  font.size=12 \
  font.color=2D2D2D \
  fill=F5F7FA \
  x=50 y=320 w=620 h=100
```

### Add table for results

```bash
officecli add thesis.pptx /slide[1] --type table --prop \
  rows=3 cols=3 \
  x=50 y=180 w=620 h=200
officecli set thesis.pptx /slide[1]/table[1]/row[1]/cell[1] --prop text="모델" font="Noto Sans KR" bold=true
officecli set thesis.pptx /slide[1]/table[1]/row[1]/cell[2] --prop text="정확도" font="Noto Sans KR" bold=true
officecli set thesis.pptx /slide[1]/table[1]/row[1]/cell[3] --prop text="F1 Score" font="Noto Sans KR" bold=true
```

## Example Content (Korean)

```
제목: 한국어 자연어 처리에서의 형태소 분석 개선 방안
부제: Transformer 기반 접근법의 성능 비교 분석
본문: 본 연구에서는 사전 학습된 언어 모델을 활용하여 한국어 형태소 분석의
     정확도를 개선하는 방법을 제안한다. 실험 결과, 제안 모델은 기존
     규칙 기반 분석기 대비 F1 스코어 기준 2.3%p 향상된 성능을 보였다.
각주: * 본 실험은 세종 코퍼스 기반으로 수행되었습니다.
```

## Design Notes

- Academic slides prioritize readability — avoid decorative elements
- Use accent blue (#2962FF) only for links, key terms, and chart primaries
- Tables should use thin borders (#E0E0E0) with header row in bold
- Footnotes and citations use 10pt gray (#666666) text
- Mixed Korean/English text is common in academic contexts — ensure font fallback works
- Code blocks should use a monospace CJK-compatible font like D2Coding
